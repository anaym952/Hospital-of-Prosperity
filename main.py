########### ALWAYS MAKE CHANGES WHEN YOU ARE IN THE "BACKUP" BRANCH,
########### COMMIT THOSE CHANGES TO BACKUP WHEN IN THAT BRANCH,
########### THEN MAKE MAIN BRANCH UP TO DATE BY SWITCHING TO MAIN BRANCH AND MERGING IT WITH BACKUP

############################################ How to format prescriptions:
##################### TOP: hospital name, physical address
##################### Below: doctor name, specialization (specialization will be only displayed on patient side when patient recieves and opens the prescription)
##################### Below: patient name, age, gender, date (age and gender will only be displayed on the patient side when patient officially recieves the issued prescription)
##################### Below: Blood pressure (ex: '120/80'mmHg), pulse rate (ex: '70'bpm)
##################### Below: medicine to prescribe, space to write drug instructions/description
##################### Bottom: doctor signature (do this later with instructor)

################# CONTINUE TO WORK ON THE PATIENT SIDE OF RECIEVING PRESCRIPTIONS AND FINISH SOON!
############### ADD DOCTOR SIGNATURE TO ISSUE_PRESCRIPTIONS() LATER (WITH INSTRUCTOR'S HELP)
######################### MAKE SURE THAT USER IS LOGGED OUT BEFORE LOGGING IN AGAIN (FIX LATER)

from flask import Flask, render_template, request, redirect, url_for, session
from werkzeug.security import generate_password_hash, check_password_hash
from datetime import datetime, timedelta
import time
import random
import string

app = Flask(__name__)
app.secret_key = 'Anay Murarka'
app.config['DEBUG']=True

hospital_address = "205 Hilltop Ave."

patient_accounts = []
doctor_accounts = []
available_times_list = []
available_times_doctor_count = {'12AM-02AM':0, '02AM-04AM':0, '04AM-06AM':0, 
'06AM-08AM':0, '08AM-10AM':0, '10AM-12PM':0, 
'12PM-02PM':0, '02PM-04PM':0, '04PM-06PM':0, 
'06PM-08PM':0, '08PM-10PM':0, '10PM-12AM':0}

appointments = []
prescriptions = []
pending_payments = []
inventory = []
emergency_rooms = [
    {'room':1, 'status':'Vacant', 'occupied_by':None}, 
    {'room':2, 'status':'Vacant', 'occupied_by':None}, 
    {'room':3, 'status':'Vacant', 'occupied_by':None}, 
    {'room':4, 'status':'Vacant', 'occupied_by':None}, 
    {'room':5, 'status':'Vacant', 'occupied_by':None}, 
    {'room':6, 'status':'Vacant', 'occupied_by':None}, 
    {'room':7, 'status':'Vacant', 'occupied_by':None}, 
    {'room':8, 'status':'Vacant', 'occupied_by':None}, 
    {'room':9, 'status':'Vacant', 'occupied_by':None}, 
    {'room':10, 'status':'Vacant', 'occupied_by':None}, 
    {'room':11, 'status':'Vacant', 'occupied_by':None}, 
    {'room':12, 'status':'Vacant', 'occupied_by':None}, 
    {'room':13, 'status':'Vacant', 'occupied_by':None}, 
    {'room':14, 'status':'Vacant', 'occupied_by':None}, 
    {'room':15, 'status':'Vacant', 'occupied_by':None}, 
    ]

# session['user_role'] = None
# session['user_name'] = None
# session['logged_in'] = False


#################################################################### HOME FUNCTIONS/PAGES:

@app.route("/")
def home():
    # print(session['user_role'], session['user_name'], session['logged_in'])
    return render_template('home.html')
    

@app.route('/patient-registration', methods=['GET', 'POST'])
def register_patient():
    if request.method == 'POST':
        account_name = request.form.get('account_name', '').strip()
        age = request.form.get('age', '').strip()
        gender = request.form.get('gender', '').strip()
        phone_number = request.form.get('phone_number', '').strip()
        medical_history = request.form.get('medical_history', '').strip()
        height = request.form.get('height', '').strip()
        weight = request.form.get('weight', '').strip()
        initial_deposit = request.form.get('balance', '').strip()
        password = request.form.get('password', '').strip()

        if not all([account_name, age, gender, phone_number, medical_history, height, weight, initial_deposit, password]):
            return render_template('PRegistration(2).html', error="All fields are required!")
       
        if any(patient['account_name'] == account_name for patient in patient_accounts):
            return render_template('PRegistration(2).html', error="Account name already exists.")
       
        if account_name.startswith("Dr.") or any(char.isdigit() for char in account_name):
            return render_template('PRegistration(2).html', error="Patients' names can't start with 'Dr.' or contain digits.")
       
        try:
            age = int(age)
            initial_deposit = float(initial_deposit)
        except ValueError:
            return render_template('PRegistration(2).html', error="Age must be an integer and Initial Deposit must be a number.")

        if age <= 0 or age >= 130:
            return render_template('PRegistration(2).html', error="Invalid age.")
       
        if len(phone_number) != 10 or not phone_number.isdigit():
            return render_template('PRegistration(2).html', error="Phone number must contain exactly 10 digits.")
        
        if not(30 <= int(height) <= 275):
            return render_template('PRegistration(2).html', error="Invalid height.")
        
        if not(20 <= int(weight) <= 1000):
            return render_template('PRegistration(2).html', error="Invalid weight.")

        if initial_deposit < 0:
            return render_template('PRegistration(2).html', error="Initial deposit must be 0 or greater.")
       
        if len(password) < 5 or not any(char.isalpha() for char in password):
            return render_template('PRegistration(2).html', error="Password must contain at least one alphabetical character and be 5+ characters long.")

        hashed_password = generate_password_hash(password)
       
        patient_data = {
            'account_name': account_name,
            'age': age,
            'gender': gender,
            'phone_number': phone_number,
            'medical_history': medical_history,
            'height': height,
            'weight': weight,
            'balance': initial_deposit,
            'password': hashed_password,
            'assigned_doctor': "N/A",
            'registered_at': datetime.now().strftime('%m/%d/%Y @%I:%M %p')
        }
       
        patient_accounts.append(patient_data)
       
        return redirect(url_for('home'))
   
    return render_template('PRegistration(2).html')



@app.route('/patient-login', methods=['GET', 'POST'])
def patient_login():
    if request.method == 'POST':
        # if session.get('logged_in'):
        #     print(session['logged_in'])
        #     return render_template('patientLogin.html', error=f"User is already logged in. Logout to login with a different account")

        account_name = request.form.get('account_name', '').strip()
        password = request.form.get('password', '').strip()
        print(f"Account Name: '{account_name}', Password: '{password}'")

        if not all([account_name, password]):
            return render_template("patientLogin.html", error="All fields must be filled.")
       
        for patient in patient_accounts:
            if account_name == patient['account_name'] and check_password_hash(patient['password'], password):
                print(f"Account Name: '{account_name}', Password: '{password}'")
                session['user_role'] = 'patient'
                session['user_name'] = account_name
                session['logged_in'] = True
                print(session['user_role'], session['user_name'], session['logged_in'])
                return redirect(url_for('patient_home'))
            
        return render_template("patientLogin.html", error="Invalid name or password.")
   
    return render_template('patientLogin.html')



@app.route('/doctor-registration', methods=['GET', 'POST'])
def register_doctor():
    if request.method == 'POST':

        authentication = request.form.get('authentication', '').strip()
        account_name = request.form.get('account_name', '').strip()
        specialization = request.form.get('specialization', '').strip()
        age = request.form.get('age', '').strip()
        gender = request.form.get('gender', '').strip()
        phone_number = request.form.get('phone_number', '').strip()
        password = request.form.get('password', '').strip()
        print(f"Authentication: '{authentication}', Account Name: '{account_name}', Age: '{age}', Gender: '{gender}', Phone Number: '{phone_number}', Password: '{password}'")

        if not all([authentication, account_name, specialization, age, gender, phone_number, password]):
            return render_template('DRegistration(3).html', error="All fields are required!")

        if not authentication.isdigit():
            return render_template('DRegistration(3).html', error="Authentication must be a numeric value.")
        elif int(authentication) < 6:
            return render_template('DRegistration(3).html', error="You must have 6+ years of experience as a doctor.")
        
        print(f"{account_name}")

        if any(doctor['account_name'] == account_name for doctor in doctor_accounts):
            return render_template('DRegistration(3).html', error="Account name already exists.")
        elif not account_name.startswith('Dr. ') or any(char.isdigit() for char in account_name):
            return render_template('DRegistration(3).html', error="Doctors' account names must start with 'Dr. ' and can't contain a digit.")
        
        if not specialization:
            return render_template('DRegistration(3).html', error="Please specify your field of specialization.")
        
        if int(age) < 30 or int(age) >= 80:
            return render_template('DRegistration(3).html', error="You must be between ages 30 and 80 to work here!")

        if len(phone_number) != 10:
            return render_template('DRegistration(3).html', error="Phone number must contain 10 digits.")
                
        if not any(char.isalpha() for char in password) or len(password) < 5:
            return render_template('DRegistration(3).html', error="Password must contain at least one alphabetical character and be 5+ characters in length.")
        elif any(password == doctor['password'] for doctor in doctor_accounts):
            return render_template('DRegistration(3).html', error="Invalid password; please choose another password.")

        hashed_password = generate_password_hash(password)

        doctor_data = {
            'account_name': account_name,
            'specialization': specialization,
            'age': age,
            'gender': gender,
            'phone_number': phone_number,
            'password': hashed_password,
            'registered_at': datetime.now().strftime('%m/%d/%Y @%I:%M %p')
        }
        doctor_accounts.append(doctor_data)

        return redirect(url_for('home'))
    
    return render_template('DRegistration(3).html')



@app.route('/doctor-login', methods=['GET','POST'])
def doctor_login():
    if request.method == 'POST':
        # if session.get('logged_in'):
        #     return render_template('doctorLogin.html', error=f"User is already logged in. Logout to login with a different account")

        account_name = request.form.get('account_name', '').strip()
        password = request.form.get('password', '').strip()
        hospital_code = request.form.get('hospital_code', '').strip()
        print(f"Account Name: '{account_name}', Password: '{password}', Hospital Code: '{hospital_code}'")

        if not all([account_name, password, hospital_code]):
            return render_template("doctorLogin.html", error="All fields must be filled.")
        
        for doctor in doctor_accounts:
            if account_name == doctor['account_name'] and check_password_hash(doctor['password'], password) and hospital_code == "HospitalofProsperity@2024":
                session['user_role'] = 'doctor'
                session['user_name'] = account_name
                session['logged_in'] = True
                print(session['user_role'], session['user_name'], session['logged_in'])
                return redirect(url_for('doctor_home'))
            
        return render_template("doctorLogin.html", error="Invalid name, password, or hospital code.")

    return render_template('doctorLogin.html')



@app.route('/admin-login', methods=['GET','POST'])
def admin_login():
    if request.method == 'POST':
        # if session.get('logged_in'):
        #     return render_template('adminLogin.html', error=f"User is already logged in. Logout to login as admin")

        admin_name = request.form.get('admin_name', '').strip()
        admin_password = request.form.get('admin_password', '').strip()
        hospital_code = request.form.get('hospital_code', '').strip()
        print(f"Admin Name: '{admin_name}', Admin Password: '{admin_password}', Hospital Code: '{hospital_code}'")

        if not all([admin_name, admin_password, hospital_code]):
            return render_template("adminLogin.html", error="All fields must be filled.")
        
        if not admin_name == "Anay Murarka" or not admin_password == "hjbfvdhj'.,732vf" or not hospital_code == "HospitalofProsperity@2024":
            return render_template("adminLogin.html", error="Invalid admin name, password, or hospital code!")
        
        session['user_role'] = 'admin'
        session['user_name'] = admin_name
        session['logged_in'] = True
        print(session['user_role'], session['user_name'], session['logged_in'])

        return redirect(url_for('admin_home'))
        
    return render_template('adminLogin.html')



@app.route('/logout', methods=['GET','POST'])
def logout():
    time.sleep(1)
    if not session.get('logged_in'):
        return "Unable to log out as user isn't logged in", 400
    else:
        session['user_role'] = None
        session['user_name'] = None
        session['logged_in'] = False
        session.clear()
        print(session.get('user_role'), session.get('user_name'), session.get('logged_in'))
        return redirect(url_for('home'))



############################################################ PATIENT FUNCTIONS/PAGES:

@app.route('/patient/home', methods=['GET','POST'])
def patient_home():
    if session.get('user_role') != 'patient':
        return redirect(url_for('patient_login'))
    
    return render_template('patientHomePage.html')



@app.route('/patient/deposit-money', methods=['GET','POST'])
def deposit_money():
    if session.get('user_role') != 'patient':
        return redirect(url_for('patient_login'))

    if request.method == 'POST':
        deposited_money = float(request.form.get('deposited_money', '0').strip())
        rounded_deposited_money = round(deposited_money, 2)
        account_name = session['user_name']

        for patient in patient_accounts:
            if account_name == patient['account_name']:
                if 0 < rounded_deposited_money < 1001:
                    patient['balance'] += rounded_deposited_money
                    time.sleep(1)
                    print(f"Account Name: '{account_name}', Balance: '{patient['balance']}'")
                    return render_template('depositMoney(4).html', success_message=f"You have successfully deposited ${rounded_deposited_money:.2f} into your account, {account_name}.")
                else:
                    return render_template('depositMoney(4).html', error="Invalid deposit amount.")
                
        return render_template('depositMoney(4).html', error="Account not found.")
            
    return render_template('depositMoney(4).html')



@app.route('/patient/withdraw-money', methods=['GET','POST'])
def withdraw_money():
    if session.get('user_role') != 'patient':
        return redirect(url_for('patient_login'))
    
    if request.method == 'POST':
        withdrawn_money = float(request.form.get('withdrawn_money', '0').strip())
        rounded_withdrawn_money = round(withdrawn_money, 2)
        account_name = session['user_name']

        for patient in patient_accounts:
            if account_name == patient['account_name']:
                if 0 < rounded_withdrawn_money < 1001:
                    if patient['balance'] >= rounded_withdrawn_money:
                        patient['balance'] -= rounded_withdrawn_money
                        time.sleep(1)
                        print(f"Account Name: '{account_name}', Balance: '{patient['balance']}'")
                        return render_template('withdrawMoney(5).html', success_message=f"You have successfully withdrawn ${rounded_withdrawn_money:.2f} from your account, {account_name}.")
                    else:
                        return render_template('withdrawMoney(5).html', error=f"Not enough money in your account to withdraw ${rounded_withdrawn_money:.2f}.")
                else:
                    return render_template('withdrawMoney(5).html', error="Invalid withdrawl amount.")
                
        return render_template('withdrawMoney(5).html', error="Account not found.")
            
    return render_template('withdrawMoney(5).html')



@app.route('/patient/book-appointment', methods=['GET', 'POST'])
def book_appointment():
    if session.get('user_role') != 'patient':
        return redirect(url_for('patient_login'))

    if request.method == 'POST':
        booked_appointment = request.form.get('booked_appointment', '').strip()
        booked = False
        try:
            booked_appointment = int(booked_appointment)
        except ValueError:
            error = f"Invalid appointment ID"

        print(f"Booked appointment ID: {booked_appointment}")
        print(f"Current User: {session.get('user_name')}")

        if any(appointment['patient'] == session.get('user_name') for appointment in appointments):
            error = "You can't book more than 1 appointment per day."
        else:
            for appointment in appointments:
                if booked_appointment == appointment['appointment_id'] and appointment['patient'] == "None":
                    appointment['patient'] = session.get('user_name')
                    booked = True
                    success_message = f"You have successfully booked appointment #{appointment['appointment_id']} with {appointment['doctor']} on {appointment['date']} @{appointment['time']}."
                    break

            if not booked:
                error = f"Invalid appointment to book."

        print(f"Appointments after booking attempt: {appointments}")

    return render_template(
        'bookAppointment(8).html',
        appointments=appointments,
        error=error if 'error' in locals() else None,
        success_message=success_message if 'success_message' in locals() else None
    )



def check_appointment_timing(appointments):
    current_time = datetime.now()
    for appointment in appointments:
        appointment_time = datetime.strptime(appointment['time'], '%H:%M:%S')

        if appointment_time < current_time:
            appointment['status'] = 'Complete'
            rand_number = random.randint(100,999)
            rand_letter = random.choice(string.ascii_letters)
            payment_id = f"{rand_number}{rand_letter}"
            pending_payment_data = {
                'payment_type': 'appointment',
                'payment_id': payment_id,
                'patient_to_pay': appointment['patient'],
                'amount_due': '50'
                }
            pending_payments.append(pending_payment_data)
            print(appointment)
        
check_appointment_timing(appointments)
    


################################################## SHOW A TABLE OF UPCOMING APPOINTMENTS, FIRST COLUMN HAS DOCTOR THAT LOGGED-IN PATIENT WILL HAVE APPOINTMENT WITH, SECOND IS THE APPOINTMENT DATE, THIRD IS THE TIME (AM/PM) (NO START BUTTON COLUMN BECAUSE NO LIVE APPOINTMENTS ON WEBSITE)
@app.route('/patient/view-upcoming-appointments', methods=['GET','POST'])
def view_upcoming_appointments_patient():
    if session.get('user_role') != 'patient':
        return redirect(url_for('patient_login'))
    
    check_appointment_timing(appointments)
    current_user = session.get('user_name')
    user_appointments = [appointment for appointment in appointments if appointment['patient'] == current_user and appointment['status'] == "Incomplete"]
    
    return render_template('viewUpcomingAppointmentsPatient(9).html', appointments=user_appointments)



##################################### SHOW A TABLE OF PAYMENTS TO BE DONE, FIRST COLUMN HAS PAYMENT TYPE (APPOINTMENT, PRESCRIPTION, ETC.), SECOND HAS AMOUNT DUE, NO PAY BUTTON (THAT WILL BE DONE IN PROCESS PAYMENTS!)
@app.route('/patient/pending-payments', methods=['GET','POST'])
def view_pending_payments():
    if session.get('user_role') != 'patient':
        return redirect(url_for('patient_login'))
    
    return render_template('viewPendingPayments(16).html')



#################################### FILL OUT IDEAS FOR THIS FUNCTION LATER (BUT THIS WILL NOT BE A TABLE BECAUSE IT NEEDS TO BE MORE FORMAL FOR OFFICIAL PAYMENTS)
@app.route('/patient/payment-history', methods=['GET','POST'])
def view_payment_history():
    if session.get('user_role') != 'patient':
        return redirect(url_for('patient_login'))
    
    return render_template('viewPaymentHistory(17).html')



@app.route('/patient/prescriptions', methods=['GET','POST'])
def recieve_prescriptions():
    if session.get('user_role') != 'patient':
        return redirect(url_for('patient_login'))
    
    if request.method == 'POST':
        prescription_ready = False
        prescription_to_recieve_id = request.form.get('prescription_to_recieve_id', '').strip()
        time.sleep(1.5)

        for prescription in prescriptions:
            if prescription['prescription_id'] == prescription_to_recieve_id and prescription['recieving_patient'] == session.get('user_name'):
                prescription_ready = True

                if prescription['prescription_status'] == 'Not recieved':
                    rand_number = random.randint(100,999)
                    rand_letter = random.choice(string.ascii_letters)
                    payment_id = f"{rand_number}{rand_letter}"
                    pending_payment_data = {
                        'payment_type': 'prescription',
                        'payment_id': payment_id,
                        'patient_to_pay': session.get('user_name'),
                        'amount_due': '100'
                    }
                    pending_payments.append(pending_payment_data)
                    prescription['prescription_status'] = 'Recieved'
                print(pending_payments)
                print(prescription)

        if not prescription_ready:
            error = f"Incorrect prescription ID or wrong patient."
    
    return render_template('recievePrescription(20).html',
        error=error if 'error' in locals() else None,
        prescription_ready=prescription_ready if 'prescription_ready' in locals() else None,
        hospital_address=hospital_address,
        prescriptions=prescriptions,
        prescription_to_recieve_id=prescription_to_recieve_id if 'prescription_to_recieve_id' in locals() else None,
        patient_logged_in = session.get('user_name').capitalize(),
        doctor_accounts=doctor_accounts,
        patient_accounts=patient_accounts
        )



@app.route('/patient/process-payments', methods=['GET','POST'])
def process_payments():
    if session.get('user_role') != 'patient':
        return redirect(url_for('patient_login'))
    
    return render_template('processPayments(21).html')



@app.route('/patient/portal', methods=['GET','POST'])
def view_patient_portal():
    if session.get('user_role') != 'patient':
        return redirect(url_for('patient_login'))
    
    return render_template('viewPatientPortal(22).html', patients=patient_accounts)



################################################################## DOCTOR FUNCTIONS/PAGES:

@app.route('/doctor/home', methods=['GET','POST'])
def doctor_home():
    if session.get('user_role') != 'doctor':
        return redirect(url_for('doctor_login'))
    
    return render_template('doctorHomePage.html')



@app.route('/doctor/availability', methods=['GET','POST'])
def send_availability():
    if session.get('user_role') != 'doctor':
        return redirect(url_for('doctor_login'))

    if request.method == 'POST':
        available_timings = request.form.getlist('available_timings')

        if not available_timings:
            return render_template('doctorAvailability(6).html', error="Please select at least one slot.")
        
        if any(session['user_name'] == doctor['name'] for doctor in available_times_list if len(available_times_list) > 0):
            print(available_times_list)
            return render_template('doctorAvailability(6).html', error="Your availability for tomorrow has already been added.")
            
        doctor_availability = {'name': session['user_name']}
        for timing in available_timings:
            doctor_availability[timing] = 'Not assigned'
        available_times_list.append(doctor_availability)
        print(available_times_list)

        return render_template('doctorAvailability(6).html', success_message="Availability for tomorrow updated successfully.")

    return render_template('doctorAvailability(6).html')



################################################## SHOW A TABLE OF UPCOMING APPOINTMENTS, FIRST COLUMN HAS PATIENT THAT LOGGED-IN DOCTOR IS HAVING APPOINTMENT WITH, SECOND IS THE APPOINTMENT DATE & TIME (NO START BUTTON COLUMN BECAUSE NO LIVE APPOINTMENTS ON WEBSITE)
@app.route('/doctor/view-upcoming-appointments', methods=['GET','POST'])
def view_upcoming_appointments_doctor():
    if session.get('user_role') != 'doctor':
        return redirect(url_for('doctor_login'))
    
    current_user = session.get('user_name')
    user_appointments = [appointment for appointment in appointments if appointment['doctor'] == current_user and appointment['patient'] != 'None' and appointment['status'] == "Incomplete"]
    
    return render_template('viewUpcomingAppointmentsDoctor(9).html', appointments=user_appointments)



@app.route('/doctor/issue-prescriptions', methods=['GET','POST'])
def issue_prescriptions():
    if session.get('user_role') != 'doctor':
        return redirect(url_for('doctor_login'))
    
    if request.method == 'POST':
        valid_prescription = True

        recieving_patient = request.form.get('recieving_patient', '').strip()
        patient_blood_pressure_1 = request.form.get('patient_blood_pressure_1', '').strip()
        patient_blood_pressure_2 = request.form.get('patient_blood_pressure_2', '').strip()
        patient_pulse_rate = request.form.get('patient_pulse_rate', '').strip()
        drug_to_prescribe = request.form.get('drug_to_prescribe', '').strip()
        drug_usage_description = request.form.get('drug_usage_description', '').strip()

        if any(recieving_patient.capitalize() == prescription['recieving_patient'] for prescription in prescriptions if prescriptions != []):
            error = f"Only 1 prescription can be prescribed to each patient at a time."
            valid_prescription = False

        if not any(recieving_patient.capitalize() == patient['account_name'].capitalize() for patient in patient_accounts):
            error = f"'{recieving_patient}' is not registered in this hospital."
            valid_prescription = False

        if int(patient_blood_pressure_1) < 80 or int(patient_blood_pressure_2) < 50 or int(patient_blood_pressure_1) > 200 or int(patient_blood_pressure_2) > 140:
            error = f"Invalid blood pressure range."
            valid_prescription = False
    
        if int(patient_pulse_rate) < 40 or int(patient_pulse_rate) > 150:
            error = f"Invalid pulse rate range."
            valid_prescription = False
        
        if not any(drug_to_prescribe.capitalize() == medicine['med_name'] for medicine in inventory):
            error = f"{drug_to_prescribe.capitalize()} not found in medicine inventory."
            valid_prescription = False

        for medicine in inventory:
            if drug_to_prescribe.capitalize() == medicine['med_name'] and medicine['med_status'] == "Expired" or drug_to_prescribe.capitalize() == medicine['med_name'] and int(medicine['med_quantity']) < 1:
                error = f"{drug_to_prescribe.capitalize()} is either expired or out of stock."
                valid_prescription = False
        
        if valid_prescription:
            patient_blood_pressure = f"{patient_blood_pressure_1}/{patient_blood_pressure_2}"

            random_number = random.randint(10,99)
            random_letter = random.choice(string.ascii_letters)
            prescription_id = f"{random_number}{random_letter}"

            prescription_data = {
                'prescription_id': prescription_id,
                'issued_by_doctor': session.get('user_name'),
                'recieving_patient': recieving_patient.capitalize(),
                'prescription_issued_date': datetime.now().strftime('%m/%d/%Y'),
                'patient_blood_pressure': patient_blood_pressure,
                'patient_pulse_rate': patient_pulse_rate,
                'drug_to_prescribe': drug_to_prescribe,
                'drug_usage_description': drug_usage_description,
                'prescription_status': 'Not recieved'
            }
            prescriptions.append(prescription_data)
            print(prescriptions)

            for medicine in inventory:
                if drug_to_prescribe.capitalize() == medicine['med_name']:
                    medicine['med_quantity'] = int(medicine['med_quantity'])
                    medicine['med_quantity'] -= 1
            print(inventory)

            success_message = f"Prescription {prescription_id} has been successfully created and issued to {recieving_patient.capitalize()}."


    return render_template('issuePrescriptions.html',
        error=error if 'error' in locals() else None,
        success_message=success_message if 'success_message' in locals() else None,
        hospital_address=hospital_address,
        today_date=datetime.now().strftime('%m/%d/%Y')
    )



@app.route('/doctor/add-patient-records', methods=['GET','POST'])
def add_patient_records():
    if session.get('user_role') != 'doctor':
        return redirect(url_for('doctor_login'))

    return render_template('addPatientsRecords(11).html')



@app.route('/doctor/view-patient-records', methods=['GET','POST'])
def view_patient_records():
    if session.get('user_role') != 'doctor':
        return redirect(url_for('doctor_login'))
    
    return render_template('viewPatientsRecords(12).html')



##################################################################### ADMIN FUNCTIONS/PAGES:

@app.route('/admin/home', methods=['GET','POST'])
def admin_home():
    if session.get('user_role') != 'admin':
        return redirect(url_for('admin_login'))
    
    return render_template('adminHomePage.html')



@app.route('/admin/view-all-accounts', methods=['GET', 'POST'])
def view_all_accounts():
    if session.get('user_role') != 'admin':
        return redirect(url_for('admin_login'))
    
    if request.method == 'POST':
        account_type = request.form.get('account_type', '').strip()

        if not account_type:
            return render_template('viewAccounts(1).html', error="Account type must be chosen.")
       
        if account_type == 'Patients':
            return render_template('viewAccounts(1).html', account_type="patient", patients=patient_accounts)
       
        elif account_type == 'Doctors':
            return render_template('viewAccounts(1).html', account_type="doctor", doctors=doctor_accounts)
   
    return render_template('viewAccounts(1).html')



@app.route('/admin/manage-doctor-availability', methods=['GET', 'POST'])
def manage_doctor_availability():
    if session.get('user_role') != 'admin':
        return redirect(url_for('admin_login'))

    if request.method == 'POST':
        timing = request.form.get('timing')
        assigned = False

        for doctor in available_times_list:
            if doctor.get(timing) == 'Not assigned' and available_times_doctor_count[timing] < 3:
                doctor[timing] = 'Assigned'  
                available_times_doctor_count[timing] += 1  
                assigned = True
                success_message = f"{doctor['name']} successfully assigned to {timing}."
                print(available_times_doctor_count)
                print(available_times_list)
                open_appointment = {
                'appointment_id':random.randint(100,999),
                'doctor':doctor['name'],
                'date':(datetime.now()+timedelta(days=1)).strftime('%m/%d/%Y'), 
                'time':timing[0:4],
                'patient':'None',
                'status':'Incomplete'
                }
                appointments.append(open_appointment)
                break  
        if not assigned:
            error = "No available doctors to assign."
    
    print(appointments)

    return render_template(
        'manageDoctorAvailability.html',
        available_times_doctor_count=available_times_doctor_count,
        available_times_list=available_times_list,
        error=error if 'error' in locals() else None,
        success_message=success_message if 'success_message' in locals() else None
    )



@app.route('/admin/assign-patient', methods=['GET', 'POST'])
def assign_patient_to_doctor():
    if session.get('user_role') != 'admin':
        return redirect(url_for('admin_login'))
    
    if request.method == 'POST':
        patient_name = request.form.get('patient_name', '').strip()
        patient = next((p for p in patient_accounts if p['account_name'].capitalize() == patient_name.capitalize()), None)

        if not patient:
            return render_template('assignPatient(7).html', error="Patient not found.", patients=patient_accounts)
       
        if not doctor_accounts:
            return render_template('assignPatient(7).html', error="No doctors have been registered yet.", patients=patient_accounts)

        if patient['assigned_doctor'] != "N/A":
            return render_template('assignPatient(7).html', error="Patient has already been assigned to a doctor.", patients=patient_accounts)

        doctor_to_assign = random.choice(doctor_accounts)
        patient['assigned_doctor'] = doctor_to_assign['account_name']

        print(f"{patient['account_name']} has been assigned to {doctor_to_assign['account_name']}.")

        success_message = f"{patient['account_name']} has been assigned to {doctor_to_assign['account_name']}."
        return render_template('assignPatient(7).html', success_message=success_message, patients=patient_accounts)

    return render_template('assignPatient(7).html', patients=patient_accounts)



@app.route('/admin/add-to-inventory', methods=['GET','POST'])
def add_to_inventory():
    if session.get('user_role') != 'admin':
        return redirect(url_for('admin_login'))
    
    if request.method == 'POST':
        new_med_name = request.form.get('new_med_name', '').strip()
        med_status = request.form.get('med_status', '').strip()
        med_quantity = request.form.get('med_quantity', '').strip()

        time.sleep(1)

        if not all([new_med_name, med_status, med_quantity]):
            return render_template('addToInventory(13).html', error="All medicine properties are required!")
        
        if any(new_med_name.capitalize() == medicine['med_name'] for medicine in inventory):
            return render_template('addToInventory(13).html', error="Only new medicines can be added to inventory. To update an existing medicine, go to 'Update Inventory'.")
       
        if not med_quantity.isnumeric():
            return render_template('addToInventory(13).html', error="Medicine quantity must be a positive integer.")
        
        if int(med_quantity) <= 0 or int(med_quantity) > 100:
            return render_template('addToInventory(13).html', error="Invalid medicine quantity.")
        
        new_med_data = {
            'med_name': new_med_name.capitalize(),
            'med_status': med_status,
            'med_quantity': med_quantity
        }
        inventory.append(new_med_data)
        print(inventory)
        return render_template('addToInventory(13).html', success_message=f"{new_med_name.capitalize()} has been successfully added to the inventory!")

    return render_template('addToInventory(13).html')



@app.route('/admin/update-inventory', methods=['GET','POST'])
def update_inventory():
    if session.get('user_role') != 'admin':
        return redirect(url_for('admin_login'))
    
    if request.method == 'POST':
        med_name = request.form.get('med_name', '').strip()
        new_med_status = request.form.get('new_med_status', '').strip()
        new_med_quantity = request.form.get('new_med_quantity', '').strip()

        time.sleep(1)
    
        if not all([med_name, new_med_status, new_med_quantity]):
            return render_template('updateInventory(14).html', error="All medicine properties are required!")
    
        if all(med_name.capitalize() != medicine['med_name'] for medicine in inventory):
            return render_template('updateInventory(14).html', error="Medicine not found in inventory. To add new medicines, go to 'Add to Inventory'.")

        if not new_med_quantity.isnumeric() or int(new_med_quantity) < 0:
            return render_template('addToInventory(13).html', error="Medicine quantity must be a positive integer.")
        
        for medicine in inventory:
            if med_name.capitalize() == medicine['med_name']:
                medicine['med_status'] = new_med_status
                medicine['med_quantity'] = new_med_quantity
                print(inventory)
                return render_template('updateInventory(14).html', success_message=f"{med_name.capitalize()} has been successfully updated.")

    return render_template('updateInventory(14).html')



@app.route('/admin/view-inventory', methods=['GET','POST'])
def view_inventory():
    if session.get('user_role') != 'admin':
        return redirect(url_for('admin_login'))
    
    return render_template('viewInventory(15).html', med_inventory=inventory)



@app.route('/admin/manage-emergency-rooms', methods=['GET', 'POST'])
def manage_emergency_rooms():
    if session.get('user_role') != 'admin':
        return redirect(url_for('admin_login'))

    error = None
    success_message = None
    patient_to_assign = None
    is_patient_valid = False

    if request.method == 'POST':
        if 'patient_to_assign' in request.form:
            patient_to_assign = request.form.get('patient_to_assign', '').strip()
            patient_found = None

            for patient in patient_accounts:
                if patient['account_name'].capitalize() == patient_to_assign:
                    patient_found = patient
                    is_patient_valid = True
                    break

            for emergency_room in emergency_rooms:
                if emergency_room.get('occupied_by') == patient_to_assign:
                    error = f"{patient_to_assign} is already assigned to emergency room {emergency_room['room']}."
                    is_patient_valid = False
                    break

            if not patient_found:
                error = f"{patient_to_assign} is not registered in this hospital."
            elif not error:
                success_message = f"{patient['account_name']} is ready to be assigned to an emergency room."

        elif 'emergency_room_to_assign' in request.form:
            patient_to_assign = request.form.get('hidden_patient_name', '').strip()
            is_patient_valid = any(patient['account_name'].capitalize() == patient_to_assign for patient in patient_accounts)

            if not is_patient_valid:
                error = f"{patient_to_assign} is not registered in this hospital."
            else:
                for emergency_room in emergency_rooms:
                    if emergency_room.get('occupied_by') == patient_to_assign:
                        error = f"{patient_to_assign} is already assigned to emergency room {emergency_room['room']}."
                        break

                if not error:
                    emergency_room_to_assign = request.form.get('emergency_room_to_assign', '').strip()
                    if not emergency_room_to_assign.isdigit():
                        error = "Invalid room number."
                    else:
                        emergency_room_to_assign = int(emergency_room_to_assign)
                        room_found = None

                        for emergency_room in emergency_rooms:
                            if emergency_room['room'] == emergency_room_to_assign:
                                room_found = emergency_room
                                break

                        if room_found:
                            if room_found['status'] == "Occupied":
                                error = f"Emergency room {room_found['room']} is already occupied."
                            else:
                                room_found['status'] = "Occupied"
                                room_found['occupied_by'] = patient_to_assign
                                success_message = f"{patient_to_assign} has been successfully assigned to emergency room {room_found['room']}."
                        else:
                            error = "Emergency room doesn't exist."

    return render_template('emergencyRooms(18).html',
                           emergency_rooms=emergency_rooms,
                           error=error,
                           success_message=success_message,
                           is_patient_valid=is_patient_valid,
                           patient_to_assign=patient_to_assign,
                           )





if __name__ == '__main__':
    app.run(debug=True)