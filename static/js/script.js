let answer;

async function processPDFs() {
    let formData = new FormData();
    let pdfFiles = document.getElementById("pdf-files").files;

    for (let i = 0; i < pdfFiles.length; i++) {
        formData.append("pdf_files", pdfFiles[i]);
    }
    document.getElementById("status").innerText = "This May Take A While...";

    try {
        let response = await fetch("/process", {
            method: "POST",
            body: formData
        });
        let result = await response.json();
        let para = document.getElementById("status"); 

        if (result.message) {
            para.innerText = result.message;
            para.style.color = "green";
        } else {
            para.innerText = result.error || "Unknown error occurred.";
            para.style.color = "red";
        }
        // para.innerText = "Sorry, Error Occured While Processing PDFs!"
    } catch (error) {
        console.error("Error processing PDFs:", error);
        let para = document.getElementById("status"); 
        para.innerText = "An error occurred while processing the PDFs.";
        para.style.color = "red";
    }
}

async function askQuestion() {
    let question = document.getElementById("question").value;
    let language = document.getElementById("language").value;

    let data = new FormData();
    data.append("language", language);
    data.append("question", question);

    document.getElementById("response").innerText = "This May Take A While...";

    try {
        let response = await fetch("/ask", {
            method: "POST",
            body: data
        });
        
        let result = await response.json();
        let para = document.getElementById("response"); 

        para.innerText = result.response || result.error;
    } catch (error) {
        console.error("Error asking question:", error);
        let para = document.getElementById("response"); 
        para.innerText = "An error occurred while processing the question.";
        para.style.color = "red";
    }
}
async function generateQuestionBank() {
    let formData = new FormData();
    let pdfFiles = document.getElementById("pdf-files").files;

    for (let i = 0; i < pdfFiles.length; i++) {
        formData.append("pdf_files", pdfFiles[i]);
    }
    document.getElementById("question-bank").innerHTML = "This May Take A While...";

    try {
        let response = await fetch("/generate_question_bank_r", {
            method: "POST",
            body: formData
        });
        let result = await response.json();

        if (result.question_bank) {
            let indicatorsHTML = "";
            let slidesHTML = "";
            let index = 0;

            for (let level in result.question_bank) {
                let questions = result.question_bank[level]
                    .filter(question => question.trim() !== "")
                    .slice(0, 5); // Take only the first five questions

                indicatorsHTML += `
                    <button type="button" data-bs-target="#carouselExampleIndicators" data-bs-slide-to="${index}" 
                        class="${index === 0 ? "active" : ""}" aria-label="Slide ${index + 1}"></button>
                `;

                slidesHTML += `
                    <div class="carousel-item ${index === 0 ? "active" : ""}" style="background-color: #EEF2FF;">
                        <div class="d-flex flex-column justify-content-center align-items-center" 
                            style="max-height: 300px; overflow-y: auto; width: 100%; padding: 20px;">
                            <br>
                            <br>
                            <h2 class="text-center">${level}</h2>
                            <ul style="text-align: left; padding-left: 20px;">
                                ${questions.map(q => `<li style="margin-bottom: 5px;">${q}</li>`).join("")}
                            </ul>
                        </div>
                    </div>
                `;
                index++;
            }

            const carouselHTML = `
                <section class="background-radial-gradient d-flex align-items-center justify-content-center vh-100">
                    <div class="container d-flex justify-content-center rounded-4">
                        <div id="carouselExampleIndicators" class="carousel slide w-75 rounded-4 overflow-hidden shadow-lg" data-bs-ride="carousel">
                            <div class="carousel-indicators">
                                ${indicatorsHTML}
                            </div>
                            <div class="carousel-inner rounded-4">
                                ${slidesHTML}
                            </div>
                            <button class="carousel-control-prev" type="button" data-bs-target="#carouselExampleIndicators" data-bs-slide="prev">
                                <span class="carousel-control-prev-icon" aria-hidden="true"></span>
                                <span class="visually-hidden">Previous</span>
                            </button>
                            <button class="carousel-control-next" type="button" data-bs-target="#carouselExampleIndicators" data-bs-slide="next">
                                <span class="carousel-control-next-icon" aria-hidden="true"></span>
                                <span class="visually-hidden">Next</span>
                            </button>
                        </div>
                    </div>
                </section>
            `;

            document.getElementById("carousel-container").innerHTML = carouselHTML;

            setTimeout(() => {
                new bootstrap.Carousel(document.getElementById("carouselExampleIndicators"), {
                    interval: 7000, 
                    wrap: true     
                });
            }, 100);

            displayQuestionBank(result.question_bank);
            document.getElementById("question-bank").innerHTML = "Scroll Down to View Results!";
        } else {
            alert(result.error);
        }
    } catch (error) {
        console.error("Error generating question bank:", error);
    }
}




let pdf_content = "";
function displayQuestionBank(questionBank) {
    let output = `
        <h2 style="text-align: left; margin-bottom: 10px;">Generated Question Bank</h2>
    `;

    for (let level in questionBank) {
        output += `
            <h3 style="text-align: left; margin-top: 15px;">${level}</h3>
            <ul style="text-align: left; padding-left: 20px;">
        `;

        questionBank[level]
            .filter(question => question.trim() !== "")
            .forEach(question => {
                output += `<li style="margin-bottom: 5px;">${question}</li>`;
            });

        output += `</ul>`;
    }

    pdf_content= output;
    // console.log(pdf_content);
}



async function getDataFile() {
    try {
        // console.log(pdf_content);
        document.getElementById("dataResponse").innerHTML = 'Preparing PDF File...';
        const response = await fetch("/create_pdf_doc", {
            method: "POST",
            headers: { "Content-Type": "application/json" },
            body: JSON.stringify({ "bank": pdf_content})
        });

        const data = await response.json();
        console.log("Response:", data);
        // alert("Data File Generated In Project Directory Successfully! ✅");
        document.getElementById("dataResponse").innerHTML = 'File Has Been Mailed to Your Address!';

    } catch (error) {
        console.error("Error:", error);
    }
}

async function summarisePDF() {
    const fileInput = document.getElementById("pdf-files");
    const toneSelect = document.getElementById("tone");
    const lengthSelect = document.getElementById("length");
    const summarySection = document.getElementById("summary-section");
    const summaryResponse = document.getElementById("summary-response");
    const statusElement = document.getElementById("status");
    const language = document.getElementById("language");

    summarySection.style.display = "none";
    summaryResponse.innerHTML = "";

    if (fileInput.files.length === 0) {
        statusElement.innerText = "Please upload a PDF file.";
        statusElement.style.color = "red";
        return;
    }

    if (!toneSelect.value || !lengthSelect.value) {
        statusElement.innerText = "Please select both tone and length.";
        statusElement.style.color = "red";
        return;
    }

    const formData = new FormData();
    formData.append("pdf_file", fileInput.files[0]);
    formData.append("tone", toneSelect.value);
    formData.append("length", lengthSelect.value);
    formData.append("language", language.value);
    console.log(language.value)


    statusElement.innerText = "Summarizing your document...";
    statusElement.style.color = "black";

    try {
        const response = await fetch("/summarise_doc", {
            method: "POST",
            body: formData,
        });

        const result = await response.json();
        var data = result.response;
        data = data.replace("*"," ")

        if (result.error) {
            summaryResponse.innerHTML = `<p class="text-danger">${result.error}</p>`;
        } else {
            summaryResponse.innerHTML = `<p>${result.response}</p>`;
            summarySection.style.display = "flex";

            // Scroll to summary
            summarySection.scrollIntoView({ behavior: "smooth" });
        }

        statusElement.innerText = "Scroll Down to View Results!";
    } catch (error) {
        console.error("Summary error:", error);
        summaryResponse.innerHTML = `<p class="text-danger">An error occurred while summarizing the document.</p>`;
        statusElement.innerText = "";
    }
}

