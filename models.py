from flask_sqlalchemy import SQLAlchemy

db = SQLAlchemy()

class Account(db.Model):
    __tablename__ = 'accounts'
    id = db.Column(db.Integer, primary_key=True)
    username = db.Column(db.String(50), unique=True, nullable=False)
    password = db.Column(db.String(200), nullable=False)  # 🔧 increased size for hashed passwords
    contact = db.Column(db.String(15), nullable=False)
    fullname = db.Column(db.String(50), nullable=False)
    role = db.Column(db.Enum('user', 'worker'), nullable=False, default='user')

    def __repr__(self):
        return f"<Account {self.username} ({self.role})>"


class Worker(db.Model):
    __tablename__ = 'worker'
    id = db.Column(db.Integer, primary_key=True)
    
    gender = db.Column(db.Enum('Male', 'Female'), nullable=True)
    age = db.Column(db.String(20), nullable=True)
    location = db.Column(db.String(100), nullable=True)
    type_of_work = db.Column(db.Text, nullable=True)       # comma-separated
    availability = db.Column(db.Text, nullable=True)      # comma-separated
    income_pref = db.Column(db.Enum('per hour', 'per day', 'per month'), nullable=True)
    expected_pay = db.Column(db.String(50), nullable=True)
    languages_known = db.Column(db.Text, nullable=True)   # comma-separated


    def __repr__(self):
        return f"<Worker ID={self.id}>"


class User(db.Model):
    __tablename__ = 'users'

    id = db.Column(db.Integer, primary_key=True)  # matches Account.id
    job_requirements = db.Column(db.Text, nullable=True)
    location = db.Column(db.String(100), nullable=True)
    date_needed = db.Column(db.Date, nullable=True)
    start_time = db.Column(db.Time, nullable=True)
    end_time = db.Column(db.Time, nullable=True)
    duration = db.Column(db.Enum('weekly', 'monthly', name='duration_enum'), nullable=True)
    special_requirements = db.Column(db.Text, nullable=True)

    def __repr__(self):
        return f"<UserJobDetails ID={self.id}>"
