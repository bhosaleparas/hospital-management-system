from pythonfiles import app
from sqlalchemy import func, cast, Date
from sqlalchemy.orm import joinedload
from flask import render_template, redirect, url_for, flash, flash, get_flashed_messages, request
from datetime import datetime, date
from werkzeug.security import generate_password_hash, check_password_hash
from flask_bcrypt import check_password_hash
from pythonfiles import mail, Message
from pythonfiles import Base, session

from pythonfiles import bcrypt

from pythonfiles import db
from pythonfiles.model import Doctor
from pythonfiles.model import Patient
from pythonfiles.model import Appointment
from pythonfiles.model import Relative
from pythonfiles.model import Staff
from pythonfiles.model import Room



# HOME ROUTE
@app.route('/')
@app.route('/home')
def index():
    return render_template('home.html')


@app.route('/add_patient', methods=['GET', 'POST'])
def add_patients():
    if request.method == 'POST':
        patient_number = request.form['patientNumber']
        patient_name = request.form['patientName']
        age = request.form['patientAge']
        address = request.form['Address']
        admit_date = request.form['admit_date']
        discharge_date = request.form['discharge_date']
        remaining_fees = request.form['remaining_fees']
        room_number = request.form['roomnumber']
        relative_name = request.form['relativeName']
        relative_contact = request.form['relativecontact']

        # Check room
        room = Room.query.filter_by(room_number=room_number).first()

        if room:
            # Check if the room avilable
            if len(room.patients) < room.max_patients:
                # Create a new patient
                new_patient = Patient(
                    patient_number=patient_number,
                    patient_name=patient_name,
                    age=age,
                    address=address,
                    admit_date=datetime.strptime(admit_date, '%Y-%m-%dT%H:%M'),
                    discharge_date=datetime.strptime(
                        discharge_date, '%Y-%m-%dT%H:%M') if discharge_date else None,
                    remaining_fees=remaining_fees,
                    room_id=room.room_id
                )

                # Create a new relative
                new_relative = Relative(
                    relative_name=relative_name,
                    relative_contact_number=relative_contact,
                    patient=new_patient
                )

                # Add new patient and relative to db
                db.session.add(new_patient)
                db.session.add(new_relative)
                db.session.commit()

                flash('Patient added successfully.', 'success')
                return redirect(url_for('add_patients'), patient=new_patient, relative=new_relative)

            else:
                flash('The room is full. Please select another room.', 'danger')
                return redirect(url_for('add_patients'))
        else:
            flash('The room does not exist. Please select another room.', 'danger')
            return redirect(url_for('add_patients'))
    else:
        return render_template('patients.html', message='Room not found.')





# Route for success page
@app.route('/success_page')
def success_page():
    return 'Patient Updated Successfully!'





@app.route('/register')
def register():
    return render_template('register.html')




@app.route('/make_appointment', methods=['GET'])
def make_appointment():
    doctor_name = request.args.get('doctor_name', '')
    return render_template('appointments.html', doctor_name=doctor_name)





# Appointment ROUTE
@app.route('/set_appointment', methods=['GET', 'POST'])
def set_appointments():
    appointment_scheduled = False
    if request.method == 'POST':
        patient_name = request.form['patientName']
        doctor_name = request.form['doctor_name']
        number = request.form['number']
        appointment_date_str = request.form.get('appointmentDate')
        fees = request.form['fees']

        appointment_date = appointment_date_str

        # Check if the doctor and patient exist
        doctor = Doctor.query.filter_by(name=doctor_name).first()
        # patient = Patient.query.filter_by(patient_name=patient_name).first()
        appointment_date = datetime.strptime(
            appointment_date_str, '%Y-%m-%d').date()

        if doctor:
            # Create a new appointment
            new_appointment = Appointment(
                doctor_id=doctor.doctor_id,
                patient_number=number,
                patient_name=patient_name,
                appointment_date=appointment_date,
                fees=fees,
                status='Scheduled'
            )

            # Add and commit the new appointment
            db.session.add(new_appointment)
            db.session.commit()

            flash((' 😊😊😊 Appointment set successfully 😊😊😊', 'success'))
            appointment_scheduled = True
        else:
            flash(('🥹🥹🥹 Doctor not found 🥹🥹🥹', 'danger'))
            appointment_scheduled = False

    return render_template('appointments.html', appointment_scheduled=appointment_scheduled)


def get_doctor_name_by_id(doctor_id):
    # Assuming Doctor is your SQLAlchemy model for doctors
    doctor = Doctor.query.get(doctor_id)
    return doctor.name if doctor else None


@app.route('/appointments_by_date', methods=['POST'])
def appointments_by_date():
    if request.method == 'POST':
        date_str = request.form['dateInput']
        print("Received date from form:", date_str)  # Debug statement

        if date_str:
            date_input = datetime.strptime(date_str, '%Y-%m-%d').date()
            print("Parsed date_input:", date_input)  # Debug statement

            appointments_by_date = (
                Appointment.query
                .filter(Appointment.appointment_date == date_input)
                .options(joinedload(Appointment.doctor))
                .all()
            )

            print("Appointments for the date:",
                  appointments_by_date)  # Debug statement

            return render_template('todays.html', appointments_by_date=appointments_by_date, date_input=date_input)

        else:
            return render_template('error.html', error_message="Date input is missing.")


@app.route('/appointments_by_patient', methods=['POST'])
def appointments_by_patient():
    if request.method == 'POST':
        patient_name = request.form['patient_name']

        # Fetch appointments with related information for the specified patient name
        appointments_by_patient = (
            Appointment.query
            .filter(func.lower(Appointment.patient_name) == func.lower(patient_name))
            .filter(Appointment.status == 'Scheduled')
            .options(joinedload(Appointment.doctor))
            .all()
        )

        return render_template('patient_name.html', appointments_by_patient=appointments_by_patient)

    # Handle other cases or redirect if needed
    return render_template('appointments.html', appointments_by_patient=appointments_by_patient)


#  CONTACT ROUTE
@app.route('/contact', methods=['POST', 'GET'])
def contact():
    if request.method == 'POST':
        name = request.form['name']
        email = request.form['email']
        message_content = request.form['message']

        # Create a Message object
        msg = Message(
            subject='Contact Form Submission',
            recipients=['parasbhosale1543@gmail.com'],  # Add your email here
            body=f'Name: {name}\nEmail: {email}\n\nMessage:\n{message_content}'
        )

        try:
            # Send the email
            mail.send(msg)
            flash('Your message has been sent successfully!', 'success')
        except Exception as e:
            app.logger.error(f"Error sending email: {str(e)}")
            flash(
                'An error occurred while sending the message. Please try again later.', 'danger')

    return render_template('contactus.html')




@app.route('/doctors')
def doctor():
    doctors_data = Doctor.query.all()
    return render_template('doctors.html', doctors=doctors_data)





# DOCTOR REGISTER ROUTE
@app.route('/register_doctor', methods=['GET', 'POST'])
def registerdoctor():
    registration = False
    if request.method == 'POST':
        name = request.form['name']
        email = request.form['email']
        contact_number = request.form['contact_number']
        specialization = request.form['specialization']
        cabin_number = request.form['cabin_number']
        password = request.form['password']
        fees = float(request.form['fees'])
        # Check if the username already exists
        existing_doctor = Doctor.query.filter_by(name=name).first()

        if existing_doctor:
            flash(('Email already exists', 'danger'))
            registration = False
            return redirect(url_for('registerdoctor', registration=registration))
        else:
            # Hash the password before storing it
            hashed_password = bcrypt.generate_password_hash(
                'password').decode('utf-8')

            new_doctor = Doctor(
                name=name,
                email=email,
                contact_number=contact_number,
                specialization=specialization,
                cabin_number=cabin_number,
                password=hashed_password,
                fees=fees
            )
            db.session.add(new_doctor)
            db.session.commit()

            flash(('Registration successful. You can now log in.', 'success'))
            registration = True
            # Redirect to the login page
            return render_template('login_doctor.html', registration=registration)

    return render_template('register_doctor.html', registration=registration)


@app.route('/login')
def login():
    return render_template('login.html')



# LOGIN ROUTE
# @app.route('/logindoctor', methods=['POST', 'GET'])
# def login_doctor():
#     if request.method=='POST':
#         email=request.form['email']
#         pasword=request.form['password']

#         hashed_password = bcrypt.generate_password_hash('password').decode('utf-8')

#         doctor = Doctor.query.filter_by(email=email).first()
#         if (doctor and (pasword==hashed_password)):
#         	return redirect(url_for('dashboard'))
#         else:
#             flash("Email or password is incorrect")
#             return redirect(url_for('login_doctor'))

#     return render_template('login_doctor.html')

@app.route('/logindoctor', methods=['POST', 'GET'])
def login_doctor(bcrypt=None):
    if request.method == 'POST':
        email = request.form['email']
        password = request.form['password']
        # print(email, pasword)

        # email_from_form =email
        # user = session.query(Doctor).filter(Doctor.email == email_from_form).first()
        doctor,=session.query(Doctor.Doctor).filter_by(email=email).first()
        print(doctor.name)



        if doctor:
           return redirect(url_for('dashboard', name=doctor.name))


    return render_template('login_doctor.html')






@app.route('/dashboard', methods=['GET', 'POST'])
def dashboard():
    if request.method == 'POST':
        today = date.today()
        todays_appointments = Appointment.query.filter(
            Appointment.appointment_date == today
        ).order_by(Appointment.appointment_time).all()

        return render_template('dashboard.html', todays_appointments=todays_appointments)

    elif request.method == 'POST':
        patient_name = request.form.get('patient_name')
        # Fetch patient information
        patient_info = Patient.query.filter_by(name=patient_name).first()

        if patient_info:
            # Fetch relatives information
            relatives_info = Relative.query.filter_by(patient_id=patient_info.patient_id).all()
            appointment_info = Appointment.query.filter_by(patient_id=patient_info.patient_id).first()
            return render_template('dashboard.html', patient_info=patient_info, relatives_info=relatives_info, appointment_info=appointment_info)
        else:
            flash(f'Patient with name {patient_name} not found', 'danger')
    return render_template('dashboard.html', todays_appointments=None,patient_info=None, relatives_info=None, appointment_info=None)








# ROUET FOR STAFF REGISTER
@app.route('/register_staff', methods=['GET', 'POST'])
def register_stafs():
    registration = False
    if request.method == 'POST':
        name = request.form['name']
        email = request.form['email']
        contact_number = request.form['contact_number']
        designation = request.form['designation']
        password = request.form['password']

        existing_staff = Staff.query.filter_by(name=name).first()

        if existing_staff:
            registration = False
            flash('Email already exists', 'danger')
            return render_template('staff.html', registration=registration)

        hashed_password = bcrypt.generate_password_hash(
            password).decode('utf-8')

        new_staff = Staff(
            name=name,
            email=email,
            contact_number=contact_number,
            designation=designation,
            password=hashed_password
        )

        db.session.add(new_staff)
        db.session.commit()
        flash('Staff registered successfully UYou Can Log in Now', 'success')
        registration = True

        return render_template('login_staff.html', registration=registration)

    return render_template('staff.html')





# STAFF LOGIN
@app.route('/login_staff', methods=['GET', 'POST'])
def login_staff():
    if request.method == 'POST':
        email = request.form['email']
        password_input = request.form['password']

        # Query the database for the staff
        staff = Staff.query.filter_by(email=email).first()

        if staff and check_password_hash(staff.password, password_input):
            # Login successful
            flash('Login successful', 'success')
            # Redirect to the staff dashboard or another page
            return redirect(url_for('index'))
        else:
            # Login failed
            flash('Login failed. Please check your email and password.', 'danger')

    return render_template('login_staff.html')




if __name__ == "__main__":
    app.run()








