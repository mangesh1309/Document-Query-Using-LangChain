import os
from PyPDF2 import PdfReader
from langchain.text_splitter import RecursiveCharacterTextSplitter
from langchain_google_genai import GoogleGenerativeAIEmbeddings, ChatGoogleGenerativeAI
from langchain_community.vectorstores import FAISS
from langchain.chains.question_answering import load_qa_chain
from langchain.prompts import PromptTemplate
import google.generativeai as genai
from dotenv import load_dotenv

load_dotenv()
API_KEY = os.getenv("GOOGLE_API_KEY")
genai.configure(api_key=API_KEY)

class PDFProcessor:
    def __init__(self):
        self.embeddings_model = GoogleGenerativeAIEmbeddings(model="models/embedding-001")
        self.chat_model = ChatGoogleGenerativeAI(model="gemini-1.5-flash", temperature=0.7)
    
    def get_pdf_text(self, pdf_files):
        text = ""
        for pdf in pdf_files:
            pdf_reader = PdfReader(pdf)
            for page in pdf_reader.pages:
                text += page.extract_text()
        return text

    def get_text_chunks(self, text):
        text_splitter = RecursiveCharacterTextSplitter(chunk_size=10000, chunk_overlap=1000)
        return text_splitter.split_text(text)

    def get_vector_store(self, text_chunks):
        vector_store = FAISS.from_texts(text_chunks, embedding=self.embeddings_model)
        vector_store.save_local("faiss_index")

    def get_conversational_chain(self):
        prompt_template = """
        Answer the question as detailed as possible from the provided context, make sure to provide all the details. If the answer is not in
        the provided context, just say, "The answer is not available in the context." Do not provide a wrong answer. 
        The answers should be in a human-like tone and should not sound AI-generated.\n\n
        Context:\n{context}\n
        Question:\n{question}\n
        Answer:
        """
        prompt = PromptTemplate(template=prompt_template, input_variables=["context", "question"])
        return load_qa_chain(self.chat_model, chain_type="stuff", prompt=prompt)

    def generate_question_bank(self, text):
        question_templates = {
            "Remember": "Generate exactly 5 short questions that assess recall of key concepts from the text. Use the verbs: Describe, Relate, Tell, Find.",
            "Understand": "Generate exactly 5 short questions that test comprehension of the ideas and concepts in the text. Use the verbs: Discuss, Outline, Explain, Predict.",
            "Apply": "Generate exactly 5 short questions that assess the application of information from the text to real-world situations. Use the verbs: Use, Illustrate, Complete, Solve.",
            "Analyze": "Generate exactly 5 short questions that require breaking down and drawing connections among ideas from the text. Use the verbs: Identify, Compare, Explain, Categorize.",
            "Evaluate": "Generate exactly 5 short questions that prompt justification of opinions, critiques, or assessments based on the text. Use the verbs: Decide, Prioritize, Rate, Justify.",
            "Create": "Generate exactly 5 short questions that encourage the development of new ideas or original work inspired by the text. Use the verbs: Create, Imagine, Design, Plan."

        }

        question_bank = {}
        for level, prompt in question_templates.items():
            
            query = f"Content:\n{text[:2500] if len(text) > 2500 else text[:1500]}\n\nPlease {prompt}. Don't bold any words in the response."
            response = self.chat_model.invoke(query)
            question_bank[level] = response.content.strip().split("\n") 

        return question_bank

    def answer_question(self, user_question):
        vector_store = FAISS.load_local("faiss_index", self.embeddings_model, allow_dangerous_deserialization=True)
        docs = vector_store.similarity_search(user_question)

        chain = self.get_conversational_chain()
        response = chain({"input_documents": docs, "question": user_question}, return_only_outputs=True)
        return response["output_text"]

    def summarize_document(self, text, tone="neutral", length="medium"):
        """Summarizes the extracted text using the Gemini model with customizable tone and length."""
        
        length_instruction = {
            "short": "Keep it very brief.",
            "medium": "Keep it moderately detailed.",
            "lengthy": "Provide a comprehensive and detailed summary."
        }.get(length, "Keep it moderately detailed.")

        tone_instruction = {
            "formal": "Use a formal tone.",
            "informal": "Use a casual, easy-to-understand tone.",
            "neutral": "Use a neutral and objective tone."
        }.get(tone, "Use a neutral and objective tone.")

        template = PromptTemplate(
            input_variables=["tone_instruction", "length_instruction", "text"],
            template="""
            Summarize the following document.
            {length_instruction} {tone_instruction}

            Document:
            {text}
            """
        )

        prompt = template.format(
            tone_instruction=tone_instruction,
            length_instruction=length_instruction,
            text=text
        )

        response = self.chat_model.invoke(prompt)
        return response.content.strip()

