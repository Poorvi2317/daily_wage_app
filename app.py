# app.py
from flask import Flask, render_template, request, redirect, url_for, flash, session, jsonify
from werkzeug.security import generate_password_hash, check_password_hash
from models import db, Account, User, Worker, Request
from datetime import datetime
import os

# ============================
#  BAGALKOT FIXED COORDINATES
# ============================
LOCATION_TO_COORDS = {
    "Navanagar, Bagalkot, Karnataka": {"lat": 16.1909, "lng": 75.7060},
    "Vidyagiri, Bagalkot, Karnataka": {"lat": 16.1760, "lng": 75.6801},
    "Neelanagar, Bagalkot, Karnataka": {"lat": 16.1823, "lng": 75.6919},
    "Sundar Nagar, Bagalkot, Karnataka": {"lat": 16.1738, "lng": 75.6707},
    "Shivarampur, Bagalkot, Karnataka": {"lat": 16.1688, "lng": 75.6690},
    "Ramnagar, Bagalkot, Karnataka": {"lat": 16.1836, "lng": 75.6967},
    "Station Road / Railway Colony, Bagalkot, Karnataka": {"lat": 16.1863, "lng": 75.6876},
    "Karnataka Bank Colony, Bagalkot, Karnataka": {"lat": 16.1754, "lng": 75.6864},
    "Old Bus Stand Area, Bagalkot, Karnataka": {"lat": 16.1746, "lng": 75.6617},
    "Chikodi Road Area, Bagalkot, Karnataka": {"lat": 16.2032, "lng": 75.6979},
    "Kalasapur, Bagalkot, Karnataka": {"lat": 16.1958, "lng": 75.6744},
    "Gandhinagar, Bagalkot, Karnataka": {"lat": 16.1828, "lng": 75.6766},
    "Sigikeri, Bagalkot, Karnataka": {"lat": 16.1500, "lng": 75.7000},
    "Simikeri, Bagalkot, Karnataka": {"lat": 16.1370, "lng": 75.7054},
    "Sirur, Bagalkot, Karnataka": {"lat": 16.1700, "lng": 75.7100},
    "Rampur, Bagalkot, Karnataka": {"lat": 16.2344, "lng": 75.7069},
    "Salagundi, Bagalkot, Karnataka": {"lat": 16.2100, "lng": 75.6550},
    "Sangapur, Bagalkot, Karnataka": {"lat": 16.2057, "lng": 75.6940},
    "Sangondi, Bagalkot, Karnataka": {"lat": 16.1977, "lng": 75.7120},
    "Sharadal, Bagalkot, Karnataka": {"lat": 16.1985, "lng": 75.6712},
    "Sidnal, Bagalkot, Karnataka": {"lat": 16.1378, "lng": 75.5288},
    "Sindagi, Bagalkot, Karnataka": {"lat": 16.2970, "lng": 75.7637},
    "Siraguppi, Bagalkot, Karnataka": {"lat": 16.2283, "lng": 75.7138},
    "Sitimani, Bagalkot, Karnataka": {"lat": 16.2148, "lng": 75.7255},
    "Sokanadgi, Bagalkot, Karnataka": {"lat": 16.2584, "lng": 75.6722},
    "Sorakopp, Bagalkot, Karnataka": {"lat": 16.2617, "lng": 75.7071},
    "Hullyal Layout, Bagalkot, Karnataka": {"lat": 16.1655, "lng": 75.6842},
    "Mallapur S L, Bagalkot, Karnataka": {"lat": 16.1539, "lng": 75.6920},
    "Budni KD, Bagalkot, Karnataka": {"lat": 16.1850, "lng": 75.6540},
    "Kodag Plot, Bagalkot, Karnataka": {"lat": 16.1907, "lng": 75.6582}
}


app = Flask(__name__, static_folder="static", template_folder="templates")
app.secret_key = os.environ.get("VETANA_SECRET", "supersecretkey")

# MySQL config — keep yours; update if needed
app.config['SQLALCHEMY_DATABASE_URI'] = "mysql+pymysql://root:2BA23CS066%402317@localhost/daily_wage_db"
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False

db.init_app(app)

with app.app_context():
    db.create_all()


# -----------------------
# Helper: get current account
# -----------------------
def current_account():
    uid = session.get("user_id")
    if not uid:
        return None
    return Account.query.get(uid)


# ------------------------------------------------
# HOME
# ------------------------------------------------
@app.route('/')
def home():
    user_id = session.get("user_id")
    role = session.get("role")

    worker_notifications = []
    user_notifications = []

    # If worker logged in → show notifications sent to him
    if user_id and role == "worker":
        worker_notifications = Request.query.filter_by(
            worker_id=user_id
        ).order_by(Request.timestamp.desc()).all()

    # If user logged in → show notifications sent by him
    if user_id and role == "user":
        user_notifications = Request.query.filter_by(
            users_id=user_id
        ).order_by(Request.timestamp.desc()).all()

    return render_template(
        "home.html",
        worker_notifications=worker_notifications,
        user_notifications=user_notifications,
        role=role
    )


# ------------------------------------------------
# SIGNIN
# ------------------------------------------------
@app.route("/signin", methods=["GET", "POST"])
def signin():
    if request.method == "POST":
        fullname = request.form.get("full_name", "").strip()
        username = request.form.get("username", "").strip()
        password = request.form.get("password", "")
        confirm_password = request.form.get("confirm_password", "")
        contact = request.form.get("mobile", "").strip()
        role = request.form.get("role", "user")

        if password != confirm_password:
            flash("Passwords do not match!", "error")
            return redirect(url_for("signin"))

        if len(password) < 6:
            flash("Password must be at least 6 characters!", "error")
            return redirect(url_for("signin"))

        if not contact.isdigit() or len(contact) != 10:
            flash("Enter a valid 10-digit mobile number!", "error")
            return redirect(url_for("signin"))

        if Account.query.filter_by(username=username).first():
            flash("Username already exists!", "error")
            return redirect(url_for("signin"))

        hashed = generate_password_hash(password)
        acc = Account(username=username, password=hashed, contact=contact, fullname=fullname, role=role)
        db.session.add(acc)
        db.session.commit()

        # create empty profile rows so User/Worker ids exist and match account id
        if role == "user":
            u = User(id=acc.id)
            db.session.add(u)
        else:
            w = Worker(id=acc.id)
            db.session.add(w)
        db.session.commit()

        session['user_id'] = acc.id
        session['username'] = acc.username
        session['role'] = acc.role

        # redirect to profile filling
        return redirect(url_for("user_page" if role == "user" else "worker_page"))

    return render_template("signin.html")


# ------------------------------------------------
# LOGIN
# ------------------------------------------------
@app.route("/login", methods=["GET", "POST"])
def login():
    if request.method == "POST":
        username = request.form.get("username")
        password = request.form.get("password")

        acc = Account.query.filter_by(username=username).first()
        if acc and check_password_hash(acc.password, password):
            session['user_id'] = acc.id
            session['username'] = acc.username
            session['role'] = acc.role
            return redirect(url_for("home"))
        flash("Invalid username or password", "error")
        return redirect(url_for("login"))

    return render_template("login.html")


# ------------------------------------------------
# LOGOUT
# ------------------------------------------------
@app.route("/logout")
def logout():
    session.clear()
    return redirect(url_for("home"))


# ------------------------------------------------
# USER PAGE
# ------------------------------------------------
@app.route("/user_page", methods=["GET", "POST"])
def user_page():
    if "user_id" not in session or session.get("role") != "user":
        return redirect(url_for("login"))

    account = Account.query.get(session["user_id"])

    if request.method == "POST":
        u = User.query.get(session["user_id"]) or User(id=session["user_id"])

        # job_requirements
        reqs = request.form.getlist("job_requirements")
        other = request.form.get("job_other")
        if other:
            reqs.append(other)
        u.job_requirements = ", ".join(reqs) if reqs else None

        # LOCATION → convert to lat/lng
        selected_location = request.form.get("location")
        u.location = selected_location

        coords = LOCATION_TO_COORDS.get(selected_location)
        if coords:
            u.lat = coords["lat"]
            u.lng = coords["lng"]

        # Date & Time
        date_needed = request.form.get("date_needed")
        u.date_needed = datetime.strptime(date_needed, "%Y-%m-%d").date() if date_needed else None

        st = request.form.get("startTime")
        et = request.form.get("endTime")
        u.start_time = datetime.strptime(st, "%H:%M").time() if st else None
        u.end_time = datetime.strptime(et, "%H:%M").time() if et else None

        # Duration
        u.duration = (request.form.get("duration") or "").lower() if request.form.get("duration") else None

        # Special Requirements
        special = request.form.getlist("special_requirements")
        other_special = request.form.get("special_other")
        if other_special:
            special.append(other_special)
        u.special_requirements = ", ".join(special) if special else None

        db.session.add(u)
        db.session.commit()

        flash("User profile updated", "success")
        return redirect(url_for("profile"))

    return render_template("user_page.html", account=account)



# ------------------------------------------------
# WORKER PAGE
# ------------------------------------------------
@app.route("/worker_page", methods=["GET", "POST"])
def worker_page():
    if "user_id" not in session or session.get("role") != "worker":
        return redirect(url_for("login"))

    account = Account.query.get(session["user_id"])

    if request.method == "POST":
        w = Worker.query.get(session["user_id"]) or Worker(id=session["user_id"])

        # Gender + Age
        w.gender = request.form.get("gender")
        w.age = request.form.get("age")

        # LOCATION → convert to lat/lng
        selected_location = request.form.get("location")
        w.location = selected_location

        coords = LOCATION_TO_COORDS.get(selected_location)
        if coords:
            w.lat = coords["lat"]
            w.lng = coords["lng"]

        # Type of Work
        types = request.form.getlist("type_of_work")
        other = request.form.get("work_other")
        if other:
            types.append(other)
        w.type_of_work = ", ".join(types) if types else None

        # Availability, Income Preference, Expected Pay, Languages
        w.availability = ", ".join(request.form.getlist("availability")) or None
        w.income_pref = request.form.get("income_pref")
        w.expected_pay = request.form.get("expected_pay")
        w.languages_known = ", ".join(request.form.getlist("languages_known")) or None

        db.session.add(w)
        db.session.commit()

        flash("Worker profile updated", "success")
        return redirect(url_for("profile"))

    return render_template("worker_page.html", account=account)


# ------------------------------------------------
# PROFILE PAGE
# ------------------------------------------------
@app.route('/profile')
def profile():
    if "user_id" not in session:
        return redirect(url_for("signin"))

    user_id = session["user_id"]

    account = Account.query.get(user_id)
    user = User.query.filter_by(id=user_id).first()
    worker = Worker.query.filter_by(id=user_id).first()

    sent_requests = Request.query.filter_by(users_id=user_id).all()
    received_requests = Request.query.filter_by(worker_id=user_id).all()

    return render_template(
        "profile.html",
        account=account,
        user=user,
        worker=worker,
        sent_requests=sent_requests,
        received_requests=received_requests
    )


@app.route("/update_profile", methods=["POST"])
def update_profile():
    if "user_id" not in session:
        return redirect(url_for("signin"))

    uid = session["user_id"]
    role = session["role"]

    acc = Account.query.get(uid)

    # ------------- ACCOUNT DETAILS (common) -------------
    acc.username = request.form.get("username") or acc.username
    acc.fullname = request.form.get("fullname") or acc.fullname
    acc.contact = request.form.get("contact") or acc.contact

    def clean(v):
        if v is None or v == "" or v == "None":
            return None
        return v

    # ------------- USER PROFILE UPDATE -------------
    if role == "user":
        u = User.query.get(uid)
        if not u:
            u = User(id=uid)

        # LOCATION → convert to lat/lng
        loc = clean(request.form.get("location"))
        if loc:
            u.location = loc
            coords = LOCATION_TO_COORDS.get(loc)
            if coords:
                u.lat = coords["lat"]
                u.lng = coords["lng"]

        u.job_requirements = clean(request.form.get("job_requirements"))

        db.session.add(u)

    # ------------- WORKER PROFILE UPDATE -------------
    elif role == "worker":
        w = Worker.query.get(uid)
        if not w:
            w = Worker(id=uid)

        # LOCATION → convert to lat/lng
        loc = clean(request.form.get("location"))
        if loc:
            w.location = loc
            coords = LOCATION_TO_COORDS.get(loc)
            if coords:
                w.lat = coords["lat"]
                w.lng = coords["lng"]

        w.gender = clean(request.form.get("gender"))
        w.age = clean(request.form.get("age"))
        w.type_of_work = clean(request.form.get("type_of_work"))
        w.availability = clean(request.form.get("availability"))
        w.income_pref = clean(request.form.get("income_pref"))
        w.expected_pay = clean(request.form.get("expected_pay"))
        w.languages_known = clean(request.form.get("languages_known"))

        db.session.add(w)

    # Save account + profile
    db.session.add(acc)
    db.session.commit()

    flash("Profile updated", "success")
    return redirect(url_for("profile"))


# ------------------------------------------------
# SEARCH (AJAX)
# ------------------------------------------------
@app.route("/api/search")
def api_search():
    q = request.args.get("q", "").strip().lower()
    if not q:
        return jsonify({"workers": []})

    matches = []
    workers = Worker.query.filter(Worker.type_of_work.ilike(f"%{q}%")).all()
    for w in workers:
        acc = Account.query.get(w.id)
        matches.append({
            "worker_id": acc.id,
            "username": acc.username,
            "type_of_work": (w.type_of_work or ""),
            "location": w.location or "",
        })
    return jsonify({"workers": matches})


# ------------------------------------------------
# Get worker profile (AJAX)
# ------------------------------------------------
@app.route("/api/worker_profile/<int:worker_id>")
def api_worker_profile(worker_id):
    w = Worker.query.get(worker_id)
    acc = Account.query.get(worker_id)

    if not w or not acc:
        return jsonify({"error": "Not found"}), 404

    return jsonify({
        "worker_id": worker_id,
        "username": acc.username,
        "fullname": acc.fullname,
        "contact": acc.contact,
        "gender": w.gender,
        "age": w.age,
        "type_of_work": w.type_of_work,
        "expected_pay": w.expected_pay,
        "location": w.location,
        "languages_known": w.languages_known,

        # ⭐ ADD THESE TWO FIELDS
        "lat": w.lat,
        "lng": w.lng
    })



@app.route("/api/user_profile/<int:user_id>")
def api_user_profile(user_id):
    acc = Account.query.get(user_id)
    user = User.query.get(user_id)

    if not acc or not user:
        return jsonify({"error": "User not found"}), 404

    return jsonify({
        "username": acc.username,
        "fullname": acc.fullname,
        "contact": acc.contact,
        "location": user.location,
        "job_requirements": user.job_requirements,
        "special_requirements": user.special_requirements,

        # ⭐ ADD THESE TWO FIELDS
        "lat": user.lat,
        "lng": user.lng
    })

# ------------------------------------------------
# Send request (AJAX POST)
# ------------------------------------------------
@app.route("/api/send_request", methods=["POST"])
def api_send_request():
    if "user_id" not in session or session.get("role") != "user":
        return jsonify({"error": "Unauthorized"}), 403

    data = request.get_json() or {}
    worker_id = data.get("worker_id")
    if not worker_id:
        return jsonify({"error": "worker_id required"}), 400

    user_id = session["user_id"]

    if user_id == worker_id:
        return jsonify({"error": "Cannot request yourself"}), 400

    target_acc = Account.query.get(worker_id)
    if not target_acc or target_acc.role != "worker":
        return jsonify({"error": "Worker not found"}), 404

    existing = Request.query.filter_by(users_id=user_id, worker_id=worker_id).first()
    if existing:
        return jsonify({"message": "Request already exists", "status": existing.status})

    req = Request(users_id=user_id, worker_id=worker_id, status="pending")
    db.session.add(req)
    db.session.commit()
    return jsonify({"message": "Request sent", "request_id": req.id})


# ------------------------------------------------
# Notifications (AJAX)
# ------------------------------------------------
@app.route('/api/notifications')
def notifications():
    if "user_id" not in session:
        return jsonify({"error": "not_logged_in"}), 401

    uid = session["user_id"]
    role = session["role"]

    notes = []

    # ----------------------------------------------------
    # USER  → See: requests they SENT
    # ----------------------------------------------------
    if role == "user":
        reqs = Request.query.filter_by(users_id=uid).order_by(Request.timestamp.desc()).all()

        for r in reqs:
            worker_acc = Account.query.get(r.worker_id)

            notes.append({
                "worker_id": r.worker_id,
                "worker_username": worker_acc.username if worker_acc else "Unknown",
                "status": r.status,
                "time": str(r.timestamp)
            })

    # ----------------------------------------------------
    # WORKER → See: requests RECEIVED (pending + accepted)
    # ----------------------------------------------------
    elif role == "worker":
        reqs = Request.query.filter_by(worker_id=uid).order_by(Request.timestamp.desc()).all()

        for r in reqs:
            # worker SHOULD NOT SEE rejected ones
            if r.status == "rejected":
                continue

            user_acc = Account.query.get(r.users_id)

            notes.append({
                "req_id": r.id,
                "user_id": r.users_id,
                "user_username": user_acc.username if user_acc else "Unknown",
                "status": r.status,
                "time": str(r.timestamp)
            })

    return jsonify({"notifications": notes})

# ------------------------------------------------
@app.route('/api/handle_request', methods=['POST'])
def handle_request():
    data = request.get_json()

    if not data or "req_id" not in data or "action" not in data:
        return jsonify({"error": "Invalid payload"}), 400

    req_id = data["req_id"]
    action = data["action"]

    req = Request.query.get(req_id)
    if not req:
        return jsonify({"error": "Request not found"}), 404

    if "user_id" not in session or session["role"] != "worker":
        return jsonify({"error": "Not permitted"}), 403

    if action == "accepted":
        req.status = "accepted"
    elif action == "rejected":
        req.status = "rejected"
    else:
        return jsonify({"error": "Invalid action"}), 400

    db.session.commit()
    return jsonify({"message": "updated"})


# ------------------------------------------------
# Extra view pages (optional)
# ------------------------------------------------
@app.route("/view_user/<int:user_id>")
def view_user(user_id):
    user = User.query.get(user_id)
    account = Account.query.get(user_id)
    return render_template("view_user.html", user=user, account=account)


@app.route("/view_worker/<int:worker_id>")
def view_worker(worker_id):
    worker = Worker.query.get(worker_id)
    account = Account.query.get(worker_id)
    return render_template("view_worker.html", worker=worker, account=account)

@app.route("/tracking/<int:worker_id>")
def tracking_page(worker_id):
    if "user_id" not in session:
        return redirect("/signin")

    user = User.query.get(session["user_id"])
    worker = Worker.query.get(worker_id)

    if not user or not user.lat or not user.lng:
        return "User static coordinates missing", 404

    if not worker or not worker.lat or not worker.lng:
        return "Worker static coordinates missing", 404

    return render_template(
        "tracking.html",
        worker_id=worker_id,
        user_lat=user.lat,
        user_lng=user.lng,
        worker_lat=worker.lat,
        worker_lng=worker.lng
    )





# ------------------------------------------------
# Run
# ------------------------------------------------
if __name__ == "__main__":
    app.run(debug=True)
