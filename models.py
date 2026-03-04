from flask_sqlalchemy import SQLAlchemy
from werkzeug.security import generate_password_hash, check_password_hash
import random, datetime

db = SQLAlchemy()

class User(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    username = db.Column(db.String(50), unique=True, nullable=False)
    name = db.Column(db.String(100), nullable=False)
    role = db.Column(db.String(20), nullable=False)  # admin, doctor, patient
    specialization = db.Column(db.String(100), nullable=True)  # department for doctors
    contact = db.Column(db.String(100), nullable=True)
    age = db.Column(db.Integer, nullable=True)
    gender = db.Column(db.String(20), nullable=True)
    password_hash = db.Column(db.String(200), nullable=False)
    approved = db.Column(db.Boolean, default=False)   # doctors must be approved
    rejected = db.Column(db.Boolean, default=False)
    created_at = db.Column(db.DateTime, default=datetime.datetime.utcnow)

    def set_password(self, password):
        self.password_hash = generate_password_hash(password)

    def check_password(self, password):
        return check_password_hash(self.password_hash, password)


class Appointment(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    
    patient_id = db.Column(db.Integer, db.ForeignKey("user.id"))
    doctor_id = db.Column(db.Integer, db.ForeignKey("user.id"))
    
    date = db.Column(db.String(20))
    time = db.Column(db.String(20))
    status = db.Column(db.String(20), default="Pending")

    # ADD THESE TWO LINES
    treatment = db.Column(db.String(250), nullable=True)
    medicine = db.Column(db.String(250), nullable=True)

    # relationships
    patient = db.relationship("User", foreign_keys=[patient_id])
    doctor = db.relationship("User", foreign_keys=[doctor_id])

class Department(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(100), nullable=False)
    description = db.Column(db.Text)
    doctors_registered = db.Column(db.Integer, default=0)


from flask_sqlalchemy import SQLAlchemy
from werkzeug.security import generate_password_hash, check_password_hash
import random, datetime

db = SQLAlchemy()

class User(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    username = db.Column(db.String(50), unique=True, nullable=False)
    name = db.Column(db.String(100), nullable=False)
    role = db.Column(db.String(20), nullable=False)  # admin, doctor, patient
    specialization = db.Column(db.String(100), nullable=True)  # department for doctors
    contact = db.Column(db.String(100), nullable=True)
    age = db.Column(db.Integer, nullable=True)
    gender = db.Column(db.String(20), nullable=True)
    password_hash = db.Column(db.String(200), nullable=False)
    approved = db.Column(db.Boolean, default=False)   # doctors must be approved
    rejected = db.Column(db.Boolean, default=False)
    created_at = db.Column(db.DateTime, default=datetime.datetime.utcnow)

    def set_password(self, password):
        self.password_hash = generate_password_hash(password)

    def check_password(self, password):
        return check_password_hash(self.password_hash, password)


class Appointment(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    
    patient_id = db.Column(db.Integer, db.ForeignKey("user.id"))
    doctor_id = db.Column(db.Integer, db.ForeignKey("user.id"))
    
    date = db.Column(db.String(20))
    time = db.Column(db.String(20))
    status = db.Column(db.String(20), default="Pending")

    # ADD THESE TWO LINES
    treatment = db.Column(db.String(250), nullable=True)
    medicine = db.Column(db.String(250), nullable=True)

    # relationships
    patient = db.relationship("User", foreign_keys=[patient_id])
    doctor = db.relationship("User", foreign_keys=[doctor_id])

class Department(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(100), nullable=False)
    description = db.Column(db.Text)
    doctors_registered = db.Column(db.Integer, default=0)


from flask_sqlalchemy import SQLAlchemy
from werkzeug.security import generate_password_hash, check_password_hash
import random, datetime

db = SQLAlchemy()

class User(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    username = db.Column(db.String(50), unique=True, nullable=False)
    name = db.Column(db.String(100), nullable=False)
    role = db.Column(db.String(20), nullable=False)  # admin, doctor, patient
    specialization = db.Column(db.String(100), nullable=True)  # department for doctors
    contact = db.Column(db.String(100), nullable=True)
    age = db.Column(db.Integer, nullable=True)
    gender = db.Column(db.String(20), nullable=True)
    password_hash = db.Column(db.String(200), nullable=False)
    approved = db.Column(db.Boolean, default=False)   # doctors must be approved
    rejected = db.Column(db.Boolean, default=False)
    created_at = db.Column(db.DateTime, default=datetime.datetime.utcnow)

    def set_password(self, password):
        self.password_hash = generate_password_hash(password)

    def check_password(self, password):
        return check_password_hash(self.password_hash, password)


class Appointment(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    
    patient_id = db.Column(db.Integer, db.ForeignKey("user.id"))
    doctor_id = db.Column(db.Integer, db.ForeignKey("user.id"))
    
    date = db.Column(db.String(20))
    time = db.Column(db.String(20))
    status = db.Column(db.String(20), default="Pending")

    # ADD THESE TWO LINES
    treatment = db.Column(db.String(250), nullable=True)
    medicine = db.Column(db.String(250), nullable=True)

    # relationships
    patient = db.relationship("User", foreign_keys=[patient_id])
    doctor = db.relationship("User", foreign_keys=[doctor_id])

class Department(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(100), nullable=False)
    description = db.Column(db.Text)
    doctors_registered = db.Column(db.Integer, default=0)


def seed_data():
    if User.query.first():
        return  # already seeded

    # Create Admin
    admin = User(username="admin", name="System Admin", role="admin", contact="N/A", approved=True)
    admin.set_password("admin123")
    db.session.add(admin)

    # Departments
    dept_names = [
        ("Cardiology", "Heart and blood vessel treatments"),
        ("Neurology", "Brain and nervous system"),
        ("Orthopedics", "Bones and muscles"),
        ("Dermatology", "Skin and hair care"),
        ("Pediatrics", "Child health"),
        ("General Medicine", "Common ailments and checkups"),
        ("Psychiatry", "Mental health and therapy"),
        ("ENT", "Ear, Nose and Throat"),
        ("Oncology", "Cancer diagnosis and treatment")
    ]
    departments = []
    for name, desc in dept_names:
        dept = Department(name=name, description=desc)
        db.session.add(dept)
        departments.append(dept)
    db.session.commit()

    # Realistic doctor names
    doctor_names = [
        "Dr. Arjun Sen", "Dr. Priya Nair", "Dr. Rohit Malhotra", "Dr. Sneha Kapoor",
    "Dr. Vivek Chatterjee", "Dr. Meera Das", "Dr. Rakesh Banerjee", "Dr. Neha Gupta",
    "Dr. Abhishek Sharma", "Dr. Ananya Ghosh", "Dr. Sandeep Rao", "Dr. Ishita Bose",
    "Dr. Arindam Dey", "Dr. Kiran Patel", "Dr. Shruti Mishra", "Dr. Soumik Roy",
    "Dr. Amit Verma", "Dr. Nisha Sen", "Dr. Debanjan Iyer", "Dr. Pallavi Dutta",
    "Dr. Rajesh Mehta", "Dr. Ritu Gupta", "Dr. Nikhil Das", "Dr. Sweta Sharma",
    "Dr. Harsh Agarwal", "Dr. Tanvi Chatterjee", "Dr. Manoj Saha", "Dr. Rhea Banerjee",
    "Dr. Ankit Roy", "Dr. Meghna Kapoor", "Dr. Tapan Bose", "Dr. Ishani Patel",
    "Dr. Rajat Ghosh", "Dr. Ritika Dey", "Dr. Karan Sen"

    ]
    for i, name in enumerate(doctor_names, start=1):
        dept = random.choice(departments)
        doctor = User(
            username=f"doctor{i}",
            name=name,
            role="doctor",
            specialization=dept.name,
            contact = f"80000{i:05d}",
            approved=True
        )
        doctor.set_password("doc123")
        db.session.add(doctor)
        dept.doctors_registered += 1

    # Realistic patient names
    patient_names = [
       "Amit Dutta", "Riya Sen", "Kunal Agarwal", "Sneha Paul", "Rahul Verma",
    "Tanvi Iyer", "Manoj Kumar", "Pooja Sharma", "Rohini Das", "Arvind Mehta",
    "Sumit Roy", "Shreya Ghosh", "Ankit Jain", "Meghna Patel", "Tapan Saha",
    "Ishani Mitra", "Rajesh Gupta", "Ritika Mondal", "Nikhil Bansal", "Sweta Roy",
    "Aditya Nair", "Sonia Kapoor", "Vikram Sharma", "Nisha Bose", "Rohan Dey",
    "Priya Singh", "Harsh Agarwal", "Ananya Chatterjee", "Karan Mehta", "Tanushree Das",
    "Ritesh Ghosh", "Divya Patel", "Siddharth Rao", "Neha Mishra", "Aakash Roy",
    "Anjali Verma", "Raghav Iyer", "Snehal Banerjee", "Aarav Gupta", "Ishita Sen",
    "Parth Saha", "Meera Sharma", "Rohan Das", "Priyanka Dutta", "Aditya Roy",
    "Shreya Nair", "Kunal Choudhury", "Tanya Kapoor", "Vivek Ghosh", "Pooja Mehta",
    "Rishabh Singh", "Anika Patel", "Saurabh Das", "Ishani Sharma", "Rajat Bose",
    "Tanvi Roy", "Amitabh Rao", "Meghna Verma", "Karan Gupta", "Ananya Dutta",
    "Rohit Nair", "Pallavi Sharma", "Siddhant Das", "Neha Kapoor", "Arjun Sen",
    "Ritika Chatterjee", "Manish Ghosh", "Priya Patel", "Ankit Roy", "Ishita Mehta",
    "Vikram Saha", "Shreya Verma", "Aditya Bose", "Sneha Das", "Rohan Rao",
    "Divya Kapoor", "Nikhil Sharma", "Aarav Dutta", "Anjali Roy", "Tanya Ghosh",
    "Ritesh Patel", "Meera Sen", "Kunal Mehta", "Priyanka Das", "Harsh Verma",
    "Ishani Roy", "Vivek Kapoor", "Tanvi Mehta", "Raghav Sen", "Anika Sharma",
    "Saurabh Patel", "Neha Roy", "Parth Ghosh", "Shreya Das", "Aditya Mehta",
    "Rohit Roy", "Pallavi Sen", "Siddhant Verma", "Amit Sharma", "Tanushree Roy" 
    ]
    for i, name in enumerate(patient_names, start=1):
        patient = User(
            username=f"patient{i}",
            name=name,
            role="patient",
            contact = f"80000{i:05d}",
            age=random.randint(18, 65),
            gender=random.choice(["Male", "Female"]),
            approved=True
        )
        patient.set_password("pat123")
        db.session.add(patient)
    db.session.commit()

    # Random demo appointments
    doctors = User.query.filter_by(role="doctor").all()
    patients = User.query.filter_by(role="patient").all()
    for _ in range(30):
        doc = random.choice(doctors)
        pat = random.choice(patients)
        date = (datetime.date.today() + datetime.timedelta(days=random.randint(0, 7))).isoformat()
        time = f"{random.randint(10, 17)}:{random.choice(['00', '30'])}"
        appt = Appointment(doctor_id=doc.id, patient_id=pat.id, date=date, time=time)
        db.session.add(appt)

    db.session.commit()  
