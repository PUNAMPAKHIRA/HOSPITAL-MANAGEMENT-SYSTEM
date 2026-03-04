from flask import Flask, render_template, request, redirect, url_for, session, flash
from models import db, User, Appointment, Department, seed_data

app = Flask(__name__)
app.secret_key = "hospital_secret_key"
app.config["SQLALCHEMY_DATABASE_URI"] = "sqlite:///hospital.db"
app.config["SQLALCHEMY_TRACK_MODIFICATIONS"] = False

db.init_app(app)
with app.app_context():
    db.create_all()
    seed_data()




# ---------- landing page ----------
@app.route("/")
def landing():
    return render_template("landing.html")






# ---------- login ----------
@app.route("/login", methods=["GET", "POST"])
def login():
    if request.method == "POST":
        username = request.form["username"].strip()
        password = request.form["password"]
        user = User.query.filter_by(username=username).first()

        if not user or not user.check_password(password):
            flash("Invalid username or password.", "danger")
            return redirect(url_for("login"))

        if user.role == "doctor":
            if user.rejected:
                flash("Your registration was rejected by the admin.", "danger")
                return redirect(url_for("login"))
            if not user.approved:
                flash("Your account is pending admin approval.", "warning")
                return redirect(url_for("login"))

        session["user_id"] = user.id
        session["role"] = user.role
        flash(f"Welcome, {user.name}!", "success")
        return redirect(url_for(f"{user.role}_dashboard"))
    return render_template("login.html")


# ---------- register (for both patient & doctor) ----------
@app.route("/register", methods=["GET", "POST"])
def register():
    departments = Department.query.all()
    if request.method == "POST":
        name = request.form["name"].strip()
        username = request.form["username"].strip()
        password = request.form["password"]
        contact = request.form.get("contact")
        role = request.form["role"]
        age = request.form.get("age") or None
        gender = request.form.get("gender") or None
        specialization = request.form.get("specialization") or None

        if User.query.filter_by(username=username).first():
            flash("Username already exists! Choose another.", "danger")
            return redirect(url_for("register"))

        user = User(
            username=username,
            name=name,
            role=role,
            contact=contact,
            age=int(age) if age else None,
            gender=gender,
            specialization=specialization if role == "doctor" else None,
            approved=(role == "patient"),
            rejected=False
        )
        user.set_password(password)
        db.session.add(user)
        db.session.commit()

        if role == "doctor":
            flash("Doctor registration submitted. Please wait for admin approval.", "info")
        else:
            flash("Patient registered successfully! You can now log in.", "success")
        return redirect(url_for("login"))

    return render_template("register.html", departments=departments)


# ---------- admin dashboard ----------
@app.route("/admin_dashboard")
def admin_dashboard():
    if session.get("role") != "admin":
        flash("Please login as admin.", "warning")
        return redirect(url_for("login"))

    doctors = User.query.filter_by(role="doctor").all()
    patients = User.query.filter_by(role="patient").all()
    appointments = Appointment.query.order_by(Appointment.date, Appointment.time).all()

    # patients count per doctor
    doctor_patients_count = {}
    for appt in appointments:
        doctor_patients_count.setdefault(appt.doctor_id, set()).add(appt.patient_id)

    # prepare lists for template
    pending_doctors_list = [d for d in doctors if (not d.approved and not d.rejected)]
    approved_doctors = [d for d in doctors if d.approved and not d.rejected]
    rejected_doctors = [d for d in doctors if d.rejected]

    # enriched approved doctors with patient count
    for d in approved_doctors:
        d.patients_count = len(doctor_patients_count.get(d.id, set()))

    totals = {
        "total_doctors": len(doctors),
        "total_patients": len(patients),
        "pending": len(pending_doctors_list)
    }

    return render_template(
        "admin_dashboard.html",
        totals=totals,
        pending_doctors_list=pending_doctors_list,
        approved_doctors=approved_doctors,
        rejected_doctors=rejected_doctors,
        appointments=appointments,
        all_patients=patients
    )


@app.route('/admin/search', methods=['GET'])
def admin_search():
    query = request.args.get('q', '').strip()
    doctors = []
    patients = []

    if query:
        doctors = User.query.filter(
            User.role == 'doctor',
            User.name.ilike(f'%{query}%')
        ).all()
        patients = User.query.filter(
            User.role == 'patient',
            User.name.ilike(f'%{query}%')
        ).all()

    return render_template('admin_search.html', query=query, doctors=doctors, patients=patients)

# ---------- Admin: view doctor profile and appointments ----------
@app.route('/admin/doctor/<int:doctor_id>')
def admin_view_doctor(doctor_id):
    if session.get("role") != "admin":
        flash("Access denied.", "danger")
        return redirect(url_for("login"))
    doctor = User.query.get_or_404(doctor_id)
    appointments = Appointment.query.filter_by(doctor_id=doctor_id).order_by(Appointment.date, Appointment.time).all()
    return render_template("admin_view_doctor.html", doctor=doctor, appointments=appointments)


# ---------- Admin: view patient profile and appointments ----------
@app.route('/admin/patient/<int:patient_id>')
def admin_view_patient(patient_id):
    if session.get("role") != "admin":
        flash("Access denied.", "danger")
        return redirect(url_for("login"))
    patient = User.query.get_or_404(patient_id)
    appointments = Appointment.query.filter_by(patient_id=patient_id).order_by(Appointment.date, Appointment.time).all()
    return render_template("admin_view_patient.html", patient=patient, appointments=appointments)



# ---------- approve / reject ----------
@app.route('/admin/approve_doctor/<int:doctor_id>')
def approve_doctor(doctor_id):
    doc = User.query.get_or_404(doctor_id)
    doc.approved = True
    doc.rejected = False
    db.session.commit()
    flash(f"Doctor {doc.name} approved successfully!", "success")
    return redirect(url_for('admin_dashboard'))

@app.route('/admin/reject_doctor/<int:doctor_id>')
def reject_doctor(doctor_id):
    doc = User.query.get_or_404(doctor_id)
    doc.approved = False
    doc.rejected = True
    db.session.commit()
    flash(f"Doctor {doc.name} has been rejected!", "danger")
    return redirect(url_for('admin_dashboard'))


# ---------- doctor dashboard ----------
@app.route("/doctor_dashboard")
def doctor_dashboard():
    if session.get("role") != "doctor":
        flash("Please login as doctor to access this page.", "warning")
        return redirect(url_for("login"))
    doctor_id = session["user_id"]
    appointments = Appointment.query.filter_by(doctor_id=doctor_id).order_by(Appointment.date, Appointment.time).all()
    return render_template("doctor_dashboard.html", appointments=appointments)


@app.route("/update_status/<int:appointment_id>/<status>")
def update_status(appointment_id, status):
    if session.get("role") != "doctor":
        flash("Access denied.", "danger")
        return redirect(url_for("login"))
    appt = Appointment.query.get_or_404(appointment_id)
    if appt.doctor_id != session["user_id"]:
        flash("You are not authorized to update this appointment.", "danger")
        return redirect(url_for("doctor_dashboard"))
    appt.status = status
    db.session.commit()
    flash(f"Appointment marked as {status}.", "success")
    return redirect(url_for("doctor_dashboard"))

@app.route("/prescribe/<int:appointment_id>", methods=["GET", "POST"])
def prescribe(appointment_id):
    if session.get("role") != "doctor":
        flash("Access denied.", "danger")
        return redirect(url_for("login"))

    appt = Appointment.query.get_or_404(appointment_id)

    # Doctor can prescribe only for their own appointment
    if appt.doctor_id != session["user_id"]:
        flash("Unauthorized access.", "danger")
        return redirect(url_for("doctor_dashboard"))

    # ✅ FETCH COMPLETE PATIENT HISTORY (across ALL doctors)
    history = Appointment.query.filter(
        Appointment.patient_id == appt.patient_id,
        Appointment.treatment.isnot(None)
    ).order_by(Appointment.date.desc()).all()

    if request.method == "POST":
        appt.treatment = request.form["treatment"]
        appt.medicine = request.form["medicine"]
        appt.status = "Completed"
        db.session.commit()

        flash("Prescription saved successfully.", "success")
        return redirect(url_for("doctor_dashboard"))

    return render_template(
        "prescribe.html",
        appt=appt,
        history=history
    )



# ---------- patient dashboard ----------
@app.route("/patient_dashboard")
def patient_dashboard():
    if session.get("role") != "patient":
        flash("Please login as patient.", "warning")
        return redirect(url_for("login"))

    patient_id = session["user_id"]
    doctors = User.query.filter_by(role="doctor", approved=True, rejected=False).all()
    appointments = Appointment.query.filter_by(patient_id=patient_id).order_by(Appointment.date, Appointment.time).all()

    # collect all treatments (appointments that have prescriptions)
    treatments = []
    for appt in appointments:
        if appt.treatment or appt.medicine:
            treatments.append({
                "doctor_name": appt.doctor.name if appt.doctor else "Unknown",
                "date": appt.date,
                "diagnosis": appt.treatment,
                "medicines": appt.medicine,
                "remarks": appt.status
            })

    return render_template(
        "patient_dashboard.html",
        doctors=doctors,
        appointments=appointments,
        treatments=treatments
    )

@app.route("/patient_search")
def patient_search():
    if session.get("role") != "patient":
        flash("Please login as patient.", "warning")
        return redirect(url_for("login"))

    query = request.args.get("q", "").strip()

    doctors = []
    if query:
        doctors = User.query.filter(
            User.role == "doctor",
            User.approved == True,
            User.rejected == False,
            (
                User.name.ilike(f"%{query}%") |
                User.specialization.ilike(f"%{query}%")
            )
        ).all()
    else:
        doctors = User.query.filter_by(role="doctor", approved=True, rejected=False).all()

    return render_template("patient_dashboard.html", doctors=doctors)


@app.route('/admin/delete_doctor/<int:doctor_id>')
def delete_doctor(doctor_id):
    if session.get("role") != "admin":
        flash("Access denied. Admins only.", "danger")
        return redirect(url_for("login"))
    
    doctor = User.query.get_or_404(doctor_id)

    # Delete all related appointments before deleting doctor
    Appointment.query.filter_by(doctor_id=doctor_id).delete()

    # Finally delete doctor record
    db.session.delete(doctor)
    db.session.commit()

    flash(f"Doctor {doctor.name} has been deleted successfully.", "info")
    return redirect(url_for("admin_dashboard"))



# ---------- book appointment ----------
@app.route("/book/<int:doctor_id>", methods=["GET", "POST"])
def book(doctor_id):
    if session.get("role") != "patient":
        flash("Please login as patient to book.", "warning")
        return redirect(url_for("login"))
    doctor = User.query.get_or_404(doctor_id)
    if request.method == "POST":
        date = request.form["date"]
        time = request.form["time"]
        appt = Appointment(patient_id=session["user_id"], doctor_id=doctor_id, date=date, time=time)
        db.session.add(appt)
        db.session.commit()
        flash("Appointment booked successfully.", "success")
        return redirect(url_for("patient_dashboard"))
    return render_template("book_appointment.html", doctor=doctor)

@app.route("/cancel_appointment/<int:appointment_id>")
def cancel_appointment(appointment_id):
    if session.get("role") != "patient":
        flash("Access denied.", "danger")
        return redirect(url_for("login"))

    appt = Appointment.query.get_or_404(appointment_id)

    # patient can cancel only their own appointment
    if appt.patient_id != session["user_id"]:
        flash("Unauthorized action.", "danger")
        return redirect(url_for("patient_dashboard"))

    db.session.delete(appt)
    db.session.commit()

    flash("Appointment cancelled successfully.", "info")
    return redirect(url_for("patient_dashboard"))



# ---------- logout ----------
@app.route("/logout")
def logout():
    session.clear()
    flash("You have been logged out.", "info")
    return redirect(url_for("login"))


if __name__ == "__main__":
    app.run(debug=True)
