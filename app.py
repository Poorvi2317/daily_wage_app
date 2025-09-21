from flask import Flask, render_template, request, redirect, url_for, flash, session
from werkzeug.security import generate_password_hash, check_password_hash
from models import User, db, Account, Worker
from datetime import datetime

app = Flask(__name__)
app.secret_key = "supersecretkey"

# MySQL config
app.config['SQLALCHEMY_DATABASE_URI'] = "mysql+pymysql://root:2BA23CS066%402317@localhost/daily_wage_db"
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False

# Initialize SQLAlchemy with app
db.init_app(app)

# Create tables if they don't exist
with app.app_context():
    db.create_all()

# ----------------- Home Route -----------------
@app.route('/')
def home():
    if 'user_id' in session:
        if session.get('role') == 'user':
            return redirect(url_for('user_page'))
        elif session.get('role') == 'worker':
            return redirect(url_for('worker_page'))
    return render_template('home.html')

# ----------------- Sign Up Route -----------------
# ----------------- Sign Up Route -----------------
@app.route('/signin', methods=['GET', 'POST'])
def signin():
    if request.method == 'POST':
        fullname = request.form['full_name'].strip()
        username = request.form['username'].strip()
        password = request.form['password']
        confirm_password = request.form['confirm_password']
        contact = request.form['mobile'].strip()
        role = request.form.get('role', 'user')

        if password != confirm_password:
            flash("Passwords do not match!", "error")
            return redirect(url_for('signin'))
        if len(password) < 6:
            flash("Password must be at least 6 characters!", "error")
            return redirect(url_for('signin'))
        if not contact.isdigit() or len(contact) != 10:
            flash("Enter a valid 10-digit mobile number!", "error")
            return redirect(url_for('signin'))
        if Account.query.filter_by(username=username).first():
            flash("Username already exists! Choose another.", "error")
            return redirect(url_for('signin'))

        hashed_password = generate_password_hash(password)
        new_account = Account(
            fullname=fullname,
            username=username,
            password=hashed_password,
            contact=contact,
            role=role
        )
        db.session.add(new_account)
        db.session.commit()

        # Auto-login after sign-up
        session['user_id'] = new_account.id
        session['username'] = new_account.username
        session['role'] = new_account.role

        # Redirect based on role for NEW users only
        if role == 'worker':
            return redirect(url_for('worker_page'))  # fill worker details first
        else:
            return redirect(url_for('user_page'))

    return render_template('signin.html')

# ----------------- User Page Route -----------------
@app.route("/user_page", methods=["GET", "POST"])
def user_page():
    if "user_id" not in session or session.get("role") != "user":
        return redirect(url_for("login"))

    account = Account.query.get(session["user_id"])

    if request.method == "POST":
        job_requirements = ", ".join(request.form.getlist("job_requirements"))
        location = request.form.get("location")
        date_needed = request.form.get("date_needed")

        start_time_str = request.form.get("startTime")
        end_time_str = request.form.get("endTime")

        start_time = datetime.strptime(start_time_str, "%H:%M").time() if start_time_str else None
        end_time = datetime.strptime(end_time_str, "%H:%M").time() if end_time_str else None

        duration = request.form.get("duration")
        special_reqs = ", ".join(request.form.getlist("special_requirements"))

        user_entry = User.query.filter_by(id=session["user_id"]).first()
        if not user_entry:
            user_entry = User(id=session["user_id"])

        user_entry.job_requirements = job_requirements
        user_entry.location = location
        user_entry.date_needed = date_needed
        user_entry.start_time = start_time
        user_entry.end_time = end_time
        user_entry.duration = duration
        user_entry.special_requirements = special_reqs

        db.session.add(user_entry)
        db.session.commit()

        flash("Job details saved successfully!", "success")
        return redirect("#")  # Replace with profile page later

    return render_template("user_page.html")


# Temporary placeholder route for profile page
@app.route("/profile")
def profile_page_pending():
    flash("Profile page is under construction.", "info")
    return redirect(url_for("home"))


# ----------------- Login Route -----------------
@app.route('/login', methods=['GET', 'POST'])
def login():
    if request.method == 'POST':
        username = request.form.get('username')
        password = request.form.get('password')

        account = Account.query.filter_by(username=username).first()
        if account and check_password_hash(account.password, password):
            session['user_id'] = account.id
            session['role'] = account.role
            if account.role == 'user':
                return redirect(url_for('user_page'))
            else:
                return redirect(url_for('worker_page'))
        else:
            flash("Invalid username or password", "error")
            return redirect(url_for('login'))

    return render_template('login.html')


# ----------------- Logout Route -----------------
@app.route('/logout')
def logout():
    session.clear()
    flash("You have been logged out.", "success")
    return redirect(url_for('login'))


# ---------------- WORKER PAGE (formerly register) ----------------
# ---------------- WORKER PAGE ----------------
@app.route("/worker_page", methods=["GET", "POST"])
def worker_page():
    if 'user_id' not in session or session.get('role') != 'worker':
        return redirect(url_for('login'))

    if request.method == "POST":
        gender = request.form.get("gender")
        age = request.form.get("age")
        location = request.form.get("location")

        type_of_work_list = request.form.getlist("type_of_work")
        other_work = request.form.get("work_other")
        if other_work:
            type_of_work_list.append(other_work)
        type_of_work = ", ".join(type_of_work_list)

        availability = ", ".join(request.form.getlist("availability"))
        income_pref = request.form.get("income_pref")
        expected_pay = request.form.get("expected_pay")
        languages_known = ", ".join(request.form.getlist("languages_known"))

        # Save in database
        new_worker = Worker(
            gender=gender,
            age=age,
            location=location,
            type_of_work=type_of_work,
            availability=availability,
            income_pref=income_pref,
            expected_pay=expected_pay,
            languages_known=languages_known
        )

        db.session.add(new_worker)
        db.session.commit()
        flash("Job details saved successfully!", "success")
        return redirect("#")  # Replace with profile page later

    return render_template("worker_page.html")


@app.route("/view")
def view():
    workers = Worker.query.order_by(Worker.id.asc()).all()
    return render_template("view.html", workers=workers)


@app.route("/update/<int:worker_id>", methods=["POST"])
def update(worker_id):
    worker = Worker.query.get_or_404(worker_id)
    name = request.form.get("name", "").strip()
    contact = request.form.get("contact", "").strip()
    occupation = request.form.get("occupation", "").strip()
    wage = request.form.get("wage", "").strip()
    working_hours = request.form.get("working_hours", "").strip()
    location = request.form.get("location", "").strip()

    if not all([name, contact, occupation, wage, working_hours, location]):
        flash("All fields are required.", "error")
        return redirect(url_for("view"))

    if not contact.isdigit() or len(contact) != 10:
        flash("Contact number must be 10 digits.", "error")
        return redirect(url_for("view"))
    if not wage.isdigit() or int(wage) < 0:
        flash("Wage must be a positive integer.", "error")
        return redirect(url_for("view"))

    worker.name = name
    worker.contact = contact
    worker.occupation = occupation
    worker.wage = int(wage)
    worker.working_hours = working_hours
    worker.location = location

    db.session.commit()
    flash("Worker updated successfully!", "success")
    return redirect(url_for("view"))


@app.route("/delete/<int:worker_id>", methods=["POST"])
def delete(worker_id):
    worker = Worker.query.get_or_404(worker_id)
    db.session.delete(worker)
    db.session.commit()
    flash("Worker deleted.", "success")
    return redirect(url_for("view"))


# ---------------- RUN ----------------
if __name__ == "__main__":
    app.run(debug=True)
