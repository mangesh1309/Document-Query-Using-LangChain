
# DocQuery - RAG Based Document Query 
### A web application for querying documents using LangChain

## Project Overview:
1. Flask-based web application
2. User authentication with Flask-Login & SQLAlchemy
3. PDF processing with LangChain and Python
4. Question bank generation from documents
5. Vector-based document querying
6. Email-based PDF sharing

## Key Features:
1. User authentication (Signup/Login/Logout) (Flask auth)
2. Upload PDFs and extract text (LangChain, Python)
3. Generate a question bank from PDF content (LangChain)
4. Query documents using vector search (FAISS)
5. Summarize the document using LLM
6. Generate and email PDFs with extracted content (smtplib)

Landing Page:
![image](https://github.com/user-attachments/assets/9f8dff5c-b642-4f2f-a8d4-1e9f768e2f45)

Login Page:
![image](https://github.com/user-attachments/assets/93051067-6f58-4b41-98db-a1a3ee55a5fe)

Register Page:
![image](https://github.com/user-attachments/assets/d3b45833-cb22-4d06-8f42-5a93a78884db)



**1. Generate Question Bank:**
The system generates a set of five questions for each level of Bloom's Taxonomy: Knowledge, Comprehension, Application, Analysis, Synthesis, and Evaluation.
Once generated, you can easily export the question bank as a PDF for convenient access and sharing.
![image](https://github.com/user-attachments/assets/cf3b1691-5316-44fd-ad50-9fb450abc8d6)


**2. Query Over Document:**
Easily search and retrieve information from your documents using AI-powered queries. Upload your PDFs and interact with them in real-time—ask questions, extract key insights, and find relevant details instantly.
No need to manually scan through lengthy reports—let AI do the work for you!
![image](https://github.com/user-attachments/assets/4e17a041-82ee-4cb9-ada5-7514fdbb1713)


**3. Summarize Document:**
This feature allows you to summarize the document in a precise and concise manner. This harnesses the power of Gemini LLM to achieve this goal.
![image](https://github.com/user-attachments/assets/6f7ef77d-ac2c-48eb-8625-1327e3ef69e2)

## Installation and Setup:
**1. Clone this repository:**
`git clone https://github.com/mangesh1309/Document-Query-Using-LangChain.git`
`cd Document-Query-Using-LangChain`

**2. Create and activate environment:**
On Windows
`python -m venv venv`
`venv\Scripts\activate`

On macOS/Linux
`python3 -m venv venv`
`source venv/bin/activate`

**3. Install requirements:**
`pip install -r requirements.txt`

**4. Set up environment variables in .env file:**
`GEMINI_API_KEY="YOUR-KEY-HERE"`

**5. Run the application:**
`python app.py`
