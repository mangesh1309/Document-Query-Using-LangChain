import smtplib
import os
from email.mime.multipart import MIMEMultipart
from email.mime.text import MIMEText
from email.mime.base import MIMEBase
from email import encoders

mail_id = os.getenv("MY_EMAIL")
password = os.getenv("MY_PASSWORD")

MY_EMAIL = mail_id
MY_PASSWORD = password 

def send_email_with_pdf(pdf_filename, TO_EMAIL):
    if not os.path.exists(pdf_filename):
        print("❌ PDF file not found!")
        return

    msg = MIMEMultipart()
    msg["From"] = MY_EMAIL
    msg["To"] = TO_EMAIL
    msg["Subject"] = "Generated PDF Document"

    body = "Hello,\n\nThe requested PDF document is attached.\n\nBest regards."
    msg.attach(MIMEText(body, "plain"))

    with open(pdf_filename, "rb") as attachment:
        part = MIMEBase("application", "octet-stream")
        part.set_payload(attachment.read())
        encoders.encode_base64(part)
        part.add_header("Content-Disposition", f"attachment; filename={pdf_filename}")
        msg.attach(part)

    with smtplib.SMTP("smtp.gmail.com", 587) as connection:
        connection.starttls()  
        connection.login(MY_EMAIL, MY_PASSWORD)
        connection.sendmail(MY_EMAIL, TO_EMAIL, msg.as_string())

    print("✅ Email sent successfully with the PDF attachment!")
