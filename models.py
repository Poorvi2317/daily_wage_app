# models.py
from flask_sqlalchemy import SQLAlchemy

db = SQLAlchemy()

# ---------- Account ----------
class Account(db.Model):
    __tablename__ = "accounts"
    id = db.Column(db.Integer, primary_key=True)
    username = db.Column(db.String(50), unique=True, nullable=False)
    password = db.Column(db.String(500), nullable=True)
    contact = db.Column(db.String(15), nullable=True)
    fullname = db.Column(db.String(100), nullable=True)
    role = db.Column(db.Enum("user", "worker"), nullable=False, default="user")

    # relationships
    user_profile = db.relationship("User", backref="account", uselist=False)
    worker_profile = db.relationship("Worker", backref="account", uselist=False)

    def __repr__(self):
        return f"<Account {self.username} ({self.role})>"


# ---------- User ----------
# NOTE: id is a foreign key to accounts.id and is primary_key so User.id == Account.id
class User(db.Model):
    __tablename__ = "users"
    id = db.Column(db.Integer, db.ForeignKey("accounts.id"), primary_key=True)

    job_requirements = db.Column(db.Text, nullable=True)
    location = db.Column(db.String(100), nullable=True)

    lat = db.Column(db.Float, nullable=True)   # NEW
    lng = db.Column(db.Float, nullable=True)   # NEW

    date_needed = db.Column(db.Date, nullable=True)
    start_time = db.Column(db.Time, nullable=True)
    end_time = db.Column(db.Time, nullable=True)
    duration = db.Column(db.Enum("weekly", "monthly", name="duration_enum"), nullable=True)
    special_requirements = db.Column(db.Text, nullable=True)
    def __repr__(self):
        return f"<UserProfile id={self.id}>"


# ---------- Worker ----------
# NOTE: id is a foreign key to accounts.id and is primary_key so Worker.id == Account.id
class Worker(db.Model):
    __tablename__ = "worker"
    id = db.Column(db.Integer, db.ForeignKey("accounts.id"), primary_key=True)

    gender = db.Column(db.Enum("Male", "Female"), nullable=True)
    age = db.Column(db.String(20), nullable=True)
    location = db.Column(db.String(100), nullable=True)

    lat = db.Column(db.Float, nullable=True)   # NEW
    lng = db.Column(db.Float, nullable=True)   # NEW

    type_of_work = db.Column(db.Text, nullable=True)
    availability = db.Column(db.Text, nullable=True)
    income_pref = db.Column(db.Enum("per hour", "per day", "per month"), nullable=True)
    expected_pay = db.Column(db.String(50), nullable=True)
    languages_known = db.Column(db.Text, nullable=True)

    def __repr__(self):
        return f"<Worker id={self.id}>"


# ---------- Requests ----------
# Request stores who (users) requested which worker (accounts.id for worker)
class Request(db.Model):
    __tablename__ = "requests"
    id = db.Column(db.Integer, primary_key=True)

    # requester user (accounts.id)
    users_id = db.Column(db.Integer, db.ForeignKey("accounts.id"), nullable=False)

    # worker (accounts.id)
    worker_id = db.Column(db.Integer, db.ForeignKey("accounts.id"), nullable=False)

    status = db.Column(db.Enum("pending", "accepted", "rejected"), default="pending")
    timestamp = db.Column(db.DateTime, server_default=db.func.now())

    requester = db.relationship("Account", foreign_keys=[users_id], backref="sent_requests")
    worker = db.relationship("Account", foreign_keys=[worker_id], backref="received_requests")

    def __repr__(self):
        return f"<Request {self.users_id} -> {self.worker_id} : {self.status}>"
