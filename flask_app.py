from flask import Flask, request, jsonify, send_from_directory
import smtplib
from email.mime.multipart import MIMEMultipart
from email.mime.text import MIMEText
import logging
from logging.handlers import RotatingFileHandler

app = Flask(__name__)

# Set up logging
handler = RotatingFileHandler('app.log', maxBytes=10000, backupCount=1)
handler.setLevel(logging.INFO)
formatter = logging.Formatter('%(asctime)s - %(levelname)s - %(message)s')
handler.setFormatter(formatter)
app.logger.addHandler(handler)

# Department to email mapping
department_emails = {
    "Computer Science": "xxx@gmail.com",
    "Economics": "xxx@gmail.com",
    "English": "xxx@gmail.com",
    "Psychology": "xxx@gmail.com",
    "Commerce": "xxx@gmail.com",
}

def send_email(student_name, department, book_title, book_author):
    from_email = "xxx@gmail.com"
    department_email = department_emails.get(department)
    to_emails = [from_email, department_email]

    if not department_email:
        app.logger.error("No email address found for department: %s", department)
        return False

    app.logger.info("Sending email to: %s for department: %s", to_emails, department)

    subject = "Book Request Letter"
    body = (f"Dear Sir/Madam,\n\n"
        f"We are writing to inform you that a student from the {department} department has requested a new book "
        f"to be included in our library collection. Please find the details of the request below:\n\n"
        f"Student Name: {student_name}\n"
        f"Book Title: {book_title}\n"
        f"Book Author: {book_author}\n\n"
        f"We kindly request you to review this request and take the necessary actions to include the book in our library.\n\n"
        f"Thank you for your attention to this matter.\n\n"
        f"Best regards,\n"
        f"Christ University Library Team")

    msg = MIMEMultipart()
    msg['From'] = from_email
    msg['To'] = ", ".join(to_emails)
    msg['Subject'] = subject
    msg.attach(MIMEText(body, 'plain'))

    try:
        server = smtplib.SMTP('smtp.gmail.com', 587) #change if not gmail
        server.starttls()
        server.login(from_email, "password")  # Replace with actual password
        server.send_message(msg)
        server.quit()
        app.logger.info("Email sent successfully to %s", to_emails)
        return True
    except Exception as e:
        app.logger.error("Failed to send email: %s", e, exc_info=True)
        return False

@app.route('/submit_request', methods=['POST'])
def submit_request():
    data = request.json
    student_name = data.get('studentName')
    department = data.get('department')
    book_title = data.get('bookTitle')
    book_author = data.get('bookAuthor')

    app.logger.info("Received request: %s", data)

    if student_name and department and book_title and book_author:
        success = send_email(student_name, department, book_title, book_author)
        return jsonify(success=success)
    else:
        app.logger.error("Invalid request data: %s", data)
        return jsonify(success=False), 400

@app.route('/book_request')
def book_request():
    return send_from_directory(directory='.', path='book_request.html')

if __name__ == '__main__':
    app.run(port=5000)
