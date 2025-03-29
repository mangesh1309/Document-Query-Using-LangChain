from flask import Flask, request, render_template, jsonify, flash, redirect, url_for, session
from xhtml2pdf import pisa
from forms import SignupForm, LogInForm
from flask_bootstrap import Bootstrap5

from flasgger import Swagger
import os

from flask_sqlalchemy import SQLAlchemy
from werkzeug.security import generate_password_hash, check_password_hash
from flask_login import LoginManager, UserMixin, login_user, login_required, logout_user, current_user


from email_sender import send_email_with_pdf
from utils import PDFProcessor

app = Flask(__name__)
bootstrap = Bootstrap5(app)
swagger = Swagger(app)

app.config['SECRET_KEY'] = 'mangest_test'
app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///users.db'
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False


db = SQLAlchemy(app)
pdf_processor = PDFProcessor()

login_manager = LoginManager(app)
login_manager.login_view = "login"
login_manager.login_message_category = "danger"

class User(UserMixin, db.Model):
    id = db.Column(db.Integer, primary_key=True)
    first_name = db.Column(db.String(100), nullable=False)
    last_name = db.Column(db.String(100), nullable=False)
    email = db.Column(db.String(150), unique=True, nullable=False)
    password = db.Column(db.String(200), nullable=False)

@login_manager.user_loader
def load_user(user_id):
    return User.query.get(int(user_id))

with app.app_context():
    db.create_all()

@app.route("/")
def home():
    return render_template("index.html")

@app.route("/signup", methods=["GET", "POST"])
def signup():
    form = SignupForm()
    if form.validate_on_submit():
        first_name = form.first_name.data
        last_name = form.last_name.data
        email = form.email.data
        password = form.password.data

        # Check if user already exists
        existing_user = User.query.filter_by(email=email).first()
        if existing_user:
            flash('Email already registered. Please log in.', 'danger')
            return redirect(url_for('signup'))

        # Hash the password
        hashed_password = generate_password_hash(password, method='pbkdf2:sha256')

        try:
            # Create new user
            new_user = User(first_name=first_name, last_name=last_name, email=email, password=hashed_password)
            db.session.add(new_user)
            db.session.commit()
        except Exception as e:
            db.session.rollback() 
            flash("An error occurred. Please try again.", "danger")
            return redirect(url_for('signup'))
        finally:
            db.session.close() 

        flash('Signup successful! You can now log in.', 'success')
        return redirect(url_for('login'))

    return render_template("signup.html", form=form)


@app.route("/login", methods=["GET", "POST"])
def login():
    form = LogInForm()
    if form.validate_on_submit():
        email = form.email.data
        password = form.password.data

        user = User.query.filter_by(email=email).first()

        if user and check_password_hash(user.password, password):
            login_user(user)
            session["user"] = str(email)
            # flash("Login successful!", "success")
            return redirect(url_for("home"))
        else:
            flash("Invalid email or password. Please try again.", "danger")
            return redirect(url_for("login"))

    return render_template("login.html", form=form)


@app.route("/logout")
@login_required
def logout():
    logout_user()
    session.pop('user', None)
    flash("You have been logged out.", "info")
    return redirect(url_for("login"))

@app.route("/generate")
@login_required
def generate_question_bank_x():
    return render_template("generate.html")

@app.route("/query")
@login_required
def query_document():
    return render_template("query.html")

@app.route("/process", methods=["POST"])
def process():
    try:
        pdf_files = request.files.getlist("pdf_files")
        pdf_text = pdf_processor.get_pdf_text(pdf_files)
        text_chunks = pdf_processor.get_text_chunks(pdf_text)
        pdf_processor.get_vector_store(text_chunks)
        return jsonify({"message": "PDFs processed successfully!"})
    except Exception as e:
        return jsonify({"error": str(e)}), 500

@app.route("/ask", methods=["POST"])
def ask():
    try:
        user_question = request.json.get("question")
        print(user_question)
        response = pdf_processor.answer_question(user_question)
        print(response)
        return jsonify({"response": response})
    except Exception as e:
        print(e)
        return jsonify({"error": str(e)}), 500

@app.route("/generate_question_bank_r", methods=["POST"])
def generate_question_bank_route():
    try:
        pdf_files = request.files.getlist("pdf_files")
        pdf_text = pdf_processor.get_pdf_text(pdf_files)
        question_bank = pdf_processor.generate_question_bank(pdf_text)
        return jsonify({"question_bank": question_bank})
    except Exception as e:
        return jsonify({"error": str(e)}), 500

@app.route("/create_pdf_doc", methods=["POST"])
def generate_data_file():
    try:
        data = request.json
        data_content = data.get("bank", "")

        pdf_filename = "output.pdf"
        with open(pdf_filename, "wb") as pdf_file:
            pisa.CreatePDF(data_content, dest=pdf_file)

        print("✅ PDF generated successfully!")

        to_mail=current_user.email
        print(to_mail)
        send_email_with_pdf(pdf_filename, to_mail)

        return jsonify({"status": "success", "message": "PDF created and emailed!"})

    except Exception as e:
        return jsonify({"error": str(e)}), 500
    
@app.route("/summarise")
@login_required
def summarise():
    return render_template("summarise.html")


@app.route("/summarise_doc", methods=["POST"])
def summarise_doc():
    try:
        if "pdf_file" not in request.files:
            return jsonify({"error": "No file uploaded"}), 400
        
        pdf_file = request.files["pdf_file"]

        if pdf_file.filename == "":
            return jsonify({"error": "No selected file"}), 400

        file_path = os.path.join("", pdf_file.filename)
        pdf_file.save(file_path)

        pdf_text = pdf_processor.get_pdf_text([file_path])  
        summary = pdf_processor.summarize_document(pdf_text)
        print(summary)

        return jsonify({"response": summary})
    except Exception as e:
        print("Error:", e)
        return jsonify({"error": "Failed to generate summary. Please try again later."}), 500


if __name__ == "__main__":
    app.run(debug=True, use_reloader=True)