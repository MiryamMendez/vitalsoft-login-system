from flask import Flask, render_template, request, redirect, url_for, flash, jsonify, session
from flask_sqlalchemy import SQLAlchemy
from datetime import datetime, timedelta
from werkzeug.security import generate_password_hash, check_password_hash

import os
from flask import Flask, render_template, request, redirect, url_for, flash, jsonify, session
from flask_sqlalchemy import SQLAlchemy
from datetime import datetime, timedelta
from werkzeug.security import generate_password_hash, check_password_hash

app = Flask(__name__, template_folder='templates')

app.secret_key = os.environ.get('SECRET_KEY', 'your_secret_key')

# SQLite configuration
app.config['SQLALCHEMY_DATABASE_URI'] = os.environ.get('DATABASE_URL', 'sqlite:///vitalsoft.db')
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False

db = SQLAlchemy(app)

# Ensure the instance folder exists
os.makedirs('instance', exist_ok=True)

# Models
class User(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    username = db.Column(db.String(100), unique=True, nullable=False)
    password_hash = db.Column(db.String(128), nullable=False)
    role = db.Column(db.String(20), nullable=False)  # e.g., 'admin', 'doctor'

    def set_password(self, password):
        self.password_hash = generate_password_hash(password)

    def check_password(self, password):
        return check_password_hash(self.password_hash, password)

class Doctor(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    doctor_id = db.Column(db.String(10), unique=True, nullable=False)
    name = db.Column(db.String(100), nullable=False)
    specialty = db.Column(db.String(100), nullable=False)
    email = db.Column(db.String(100), nullable=False)
    phone = db.Column(db.String(20), nullable=False)
    status = db.Column(db.String(20), default='Activo')
    appointments = db.relationship('Appointment', backref='doctor', lazy=True)

    def __init__(self, doctor_id, name, specialty, email, phone, status='Activo'):
        self.doctor_id = doctor_id
        self.name = name
        self.specialty = specialty
        self.email = email
        self.phone = phone
        self.status = status

class Patient(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    patient_id = db.Column(db.String(10), unique=True, nullable=False)
    expediente = db.Column(db.String(10), unique=True, nullable=False)
    name = db.Column(db.String(100), nullable=False)
    email = db.Column(db.String(100), nullable=False)
    phone = db.Column(db.String(20), nullable=False)
    birth_date = db.Column(db.Date, nullable=False)
    blood_type = db.Column(db.String(5))
    allergies = db.Column(db.Text)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)

    def __init__(self, patient_id, expediente, name, email, phone, birth_date, blood_type=None, allergies=None):
        self.patient_id = patient_id
        self.expediente = expediente
        self.name = name
        self.email = email
        self.phone = phone
        self.birth_date = birth_date
        self.blood_type = blood_type
        self.allergies = allergies

class Medication(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(100), nullable=False)
    description = db.Column(db.Text)
    stock = db.Column(db.Integer, default=0)
    unit = db.Column(db.String(20))  # e.g., tablets, ml, etc.
    created_at = db.Column(db.DateTime, default=datetime.utcnow)

    def __init__(self, name, description=None, stock=0, unit=None):
        self.name = name
        self.description = description
        self.stock = stock
        self.unit = unit

class Prescription(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    appointment_id = db.Column(db.Integer, db.ForeignKey('appointment.id'), nullable=False)
    medication_id = db.Column(db.Integer, db.ForeignKey('medication.id'), nullable=False)
    dosage = db.Column(db.String(100), nullable=False)
    instructions = db.Column(db.Text)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)

    def __init__(self, appointment_id, medication_id, dosage, instructions=None):
        self.appointment_id = appointment_id
        self.medication_id = medication_id
        self.dosage = dosage
        self.instructions = instructions

class Appointment(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    patient_id = db.Column(db.Integer, db.ForeignKey('patient.id'), nullable=False)
    doctor_id = db.Column(db.Integer, db.ForeignKey('doctor.id'), nullable=False)
    date = db.Column(db.Date, nullable=False)
    time = db.Column(db.Time, nullable=False)
    reason = db.Column(db.Text)
    status = db.Column(db.String(20), default='Programada')
    notes = db.Column(db.Text)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    patient = db.relationship('Patient', backref=db.backref('appointments', lazy=True))
    prescriptions = db.relationship('Prescription', backref='appointment', lazy=True)

    def __init__(self, patient_id, doctor_id, date, time, reason=None, status='Programada', notes=None):
        self.patient_id = patient_id
        self.doctor_id = doctor_id
        self.date = date
        self.time = time
        self.reason = reason
        self.status = status
        self.notes = notes

# Protect routes decorator
from functools import wraps

def login_required(f):
    @wraps(f)
    def decorated_function(*args, **kwargs):
        if 'user_id' not in session:
            flash('Por favor, inicia sesión para acceder a esta página.')
            return redirect(url_for('login'))
        return f(*args, **kwargs)
    return decorated_function

# Authentication routes
@app.route('/login', methods=['GET', 'POST'])
def login():
    if request.method == 'POST':
        username = request.form['username']
        password = request.form['password']
        user = User.query.filter_by(username=username).first()
        if user and user.check_password(password):
            session['user_id'] = user.id
            session['username'] = user.username
            session['role'] = user.role
            flash('Inicio de sesión exitoso.')
            return redirect(url_for('index'))
        else:
            flash('Usuario o contraseña incorrectos.')
            return redirect(url_for('login'))
    return render_template('login.html')

@app.route('/logout')
def logout():
    session.clear()
    flash('Has cerrado sesión.')
    return redirect(url_for('login'))

@app.route('/register', methods=['GET', 'POST'])
def register_user():
    if request.method == 'POST':
        username = request.form['username']
        password = request.form['password']
        
        if not username or not password:
            flash('Por favor, complete todos los campos.')
            return redirect(url_for('register_user'))
            
        existing_user = User.query.filter_by(username=username).first()
        if existing_user:
            flash('Este correo electrónico ya está registrado.')
            return redirect(url_for('register_user'))
            
        new_user = User(username=username, role='admin')
        new_user.set_password(password)
        
        try:
            db.session.add(new_user)
            db.session.commit()
            flash('¡Registro exitoso! Por favor inicie sesión.')
            return redirect(url_for('login'))
        except:
            db.session.rollback()
            flash('Error al registrar el usuario.')
            return redirect(url_for('register_user'))
            
    return render_template('register.html')

# Routes
@app.route('/')
def home():
    if 'user_id' in session:
        return redirect(url_for('index'))
    return render_template('landing.html')

@app.route('/index')
@login_required
def index():
    patients = Patient.query.all()
    doctors = Doctor.query.all()
    appointments = Appointment.query.order_by(Appointment.date.desc()).all()
    return render_template('index.html', 
                         patients=patients,
                         doctors=doctors,
                         appointments=appointments)

# Patient Management Routes
@app.route('/patients')
@login_required
def patients():
    patients = Patient.query.all()
    now = datetime.now()
    return render_template('patients.html', patients=patients, now=now)

@app.route('/patients/add', methods=['POST'])
@login_required
def add_patient():
    if request.method == 'POST':
        # Generate unique patient ID and expediente
        last_patient = Patient.query.order_by(Patient.id.desc()).first()
        patient_num = (last_patient.id + 1) if last_patient else 1
        patient_id = f'P{str(patient_num).zfill(5)}'
        expediente = f'EXP{str(patient_num).zfill(5)}'
        
        try:
            new_patient = Patient(
                patient_id=patient_id,
                expediente=expediente,
                name=request.form['name'],
                email=request.form['email'],
                phone=request.form['phone'],
                birth_date=datetime.strptime(request.form['birth_date'], '%Y-%m-%d'),
                blood_type=request.form['blood_type'],
                allergies=request.form['allergies']
            )
            db.session.add(new_patient)
            db.session.commit()
            flash('Paciente agregado exitosamente.')
        except Exception as e:
            db.session.rollback()
            flash('Error al agregar paciente.')
            
        return redirect(url_for('patients'))

@app.route('/patients/edit/<int:id>', methods=['GET', 'POST'])
@login_required
def edit_patient(id):
    patient = Patient.query.get_or_404(id)
    if request.method == 'POST':
        try:
            patient.name = request.form['name']
            patient.email = request.form['email']
            patient.phone = request.form['phone']
            patient.birth_date = datetime.strptime(request.form['birth_date'], '%Y-%m-%d')
            patient.blood_type = request.form['blood_type']
            patient.allergies = request.form['allergies']
            db.session.commit()
            flash('Paciente actualizado exitosamente.')
            return redirect(url_for('patients'))
        except:
            db.session.rollback()
            flash('Error al actualizar paciente.')
    return render_template('edit_patient.html', patient=patient)

@app.route('/patients/delete/<int:id>')
@login_required
def delete_patient(id):
    patient = Patient.query.get_or_404(id)
    try:
        db.session.delete(patient)
        db.session.commit()
        flash('Paciente eliminado exitosamente.')
    except:
        db.session.rollback()
        flash('Error al eliminar paciente.')
    return redirect(url_for('patients'))

# Medication Management Routes
@app.route('/medications')
@login_required
def medications():
    medications = Medication.query.all()
    return render_template('medications.html', medications=medications)

@app.route('/medications/add', methods=['POST'])
@login_required
def add_medication():
    if request.method == 'POST':
        try:
            new_medication = Medication(
                name=request.form['name'],
                description=request.form['description'],
                stock=int(request.form['stock']),
                unit=request.form['unit']
            )
            db.session.add(new_medication)
            db.session.commit()
            flash('Medicamento agregado exitosamente.')
        except:
            db.session.rollback()
            flash('Error al agregar medicamento.')
        return redirect(url_for('medications'))

@app.route('/medications/edit/<int:id>', methods=['GET', 'POST'])
@login_required
def edit_medication(id):
    medication = Medication.query.get_or_404(id)
    if request.method == 'POST':
        try:
            medication.name = request.form['name']
            medication.description = request.form['description']
            medication.unit = request.form['unit']
            db.session.commit()
            flash('Medicamento actualizado exitosamente.')
            return redirect(url_for('medications'))
        except:
            db.session.rollback()
            flash('Error al actualizar medicamento.')
    return render_template('edit_medication.html', medication=medication)

@app.route('/medications/stock/<int:id>', methods=['GET', 'POST'])
@login_required
def update_medication_stock(id):
    medication = Medication.query.get_or_404(id)
    if request.method == 'POST':
        try:
            medication.stock = int(request.form['stock'])
            db.session.commit()
            flash('Stock actualizado exitosamente.')
            return redirect(url_for('medications'))
        except:
            db.session.rollback()
            flash('Error al actualizar stock.')
    return render_template('update_stock.html', medication=medication)

@app.route('/medications/delete/<int:id>')
@login_required
def delete_medication(id):
    medication = Medication.query.get_or_404(id)
    try:
        db.session.delete(medication)
        db.session.commit()
        flash('Medicamento eliminado exitosamente.')
    except:
        db.session.rollback()
        flash('Error al eliminar medicamento.')
    return redirect(url_for('medications'))

# Doctor Management Routes
@app.route('/doctors')
@login_required
def doctors():
    doctors = Doctor.query.all()
    return render_template('doctors.html', doctors=doctors)

@app.route('/doctors/add', methods=['POST'])
@login_required
def add_doctor():
    if request.method == 'POST':
        # Generate unique doctor ID
        last_doctor = Doctor.query.order_by(Doctor.id.desc()).first()
        doctor_num = (last_doctor.id + 1) if last_doctor else 1
        doctor_id = f'D{str(doctor_num).zfill(5)}'
        
        try:
            new_doctor = Doctor(
                doctor_id=doctor_id,
                name=request.form['name'],
                specialty=request.form['specialty'],
                email=request.form['email'],
                phone=request.form['phone']
            )
            db.session.add(new_doctor)
            db.session.commit()
            flash('Doctor agregado exitosamente.')
        except:
            db.session.rollback()
            flash('Error al agregar doctor.')
        return redirect(url_for('doctors'))

@app.route('/doctors/edit/<int:id>', methods=['GET', 'POST'])
@login_required
def edit_doctor(id):
    doctor = Doctor.query.get_or_404(id)
    if request.method == 'POST':
        try:
            doctor.name = request.form['name']
            doctor.specialty = request.form['specialty']
            doctor.email = request.form['email']
            doctor.phone = request.form['phone']
            doctor.status = request.form['status']
            db.session.commit()
            flash('Doctor actualizado exitosamente.')
            return redirect(url_for('doctors'))
        except:
            db.session.rollback()
            flash('Error al actualizar doctor.')
    return render_template('edit_doctor.html', doctor=doctor)

@app.route('/doctors/delete/<int:id>')
@login_required
def delete_doctor(id):
    doctor = Doctor.query.get_or_404(id)
    try:
        db.session.delete(doctor)
        db.session.commit()
        flash('Doctor eliminado exitosamente.')
    except:
        db.session.rollback()
        flash('Error al eliminar doctor.')
    return redirect(url_for('doctors'))

# Appointment Management Routes
@app.route('/records')
@login_required
def records():
    patients = Patient.query.all()
    now = datetime.now()
    return render_template('records.html', patients=patients, now=now)

@app.route('/records/<int:id>')
@login_required
def view_record(id):
    patient = Patient.query.get_or_404(id)
    appointments = Appointment.query.filter_by(patient_id=id).order_by(Appointment.date.desc()).all()
    now = datetime.now()
    return render_template('view_record.html', patient=patient, appointments=appointments, now=now)

@app.route('/appointments', methods=['GET', 'POST'])
@login_required
def appointments():
    patients = Patient.query.all()
    doctors = Doctor.query.all()
    medications = Medication.query.all()
    if request.method == 'POST':
        try:
            new_appointment = Appointment(
                patient_id=request.form['patient_id'],
                doctor_id=request.form['doctor_id'],
                date=datetime.strptime(request.form['date'], '%Y-%m-%d').date(),
                time=datetime.strptime(request.form['time'], '%H:%M').time(),
                reason=request.form['reason']
            )
            db.session.add(new_appointment)
            db.session.commit()
            
            # Add prescriptions if any
            if 'medications' in request.form:
                for med_id in request.form.getlist('medications'):
                    prescription = Prescription(
                        appointment_id=new_appointment.id,
                        medication_id=med_id,
                        dosage=request.form.get(f'dosage_{med_id}', ''),
                        instructions=request.form.get(f'instructions_{med_id}', '')
                    )
                    db.session.add(prescription)
                db.session.commit()
                
            flash('Cita programada exitosamente.')
        except Exception as e:
            db.session.rollback()
            flash('Error al programar cita.')
        return redirect(url_for('appointments'))
        
    appointments = Appointment.query.order_by(Appointment.date.desc()).all()
    return render_template('appointments.html', 
                         patients=patients,
                         doctors=doctors,
                         medications=medications,
                         appointments=appointments)

def init_db():
    with app.app_context():
        # Drop all tables
        db.drop_all()
        # Create all tables
        db.create_all()
        
        try:
            # Create admin user
            admin = User(username='admin@vitalsoft.com', role='admin')
            admin.set_password('admin123')
            db.session.add(admin)
            
            # Create sample doctors
            doctors = [
                Doctor(
                    doctor_id='D00001',
                    name='Dr. Juan Pérez',
                    specialty='Cardiología',
                    email='juan.perez@vitalsoft.com',
                    phone='555-0101'
                ),
                Doctor(
                    doctor_id='D00002',
                    name='Dra. María García',
                    specialty='Pediatría',
                    email='maria.garcia@vitalsoft.com',
                    phone='555-0102'
                ),
                Doctor(
                    doctor_id='D00003',
                    name='Dr. Carlos Rodríguez',
                    specialty='Traumatología',
                    email='carlos.rodriguez@vitalsoft.com',
                    phone='555-0103'
                )
            ]
            db.session.add_all(doctors)
            
            # Create sample medications
            medications = [
                Medication(
                    name='Paracetamol',
                    description='Analgésico y antipirético',
                    stock=100,
                    unit='tabletas'
                ),
                Medication(
                    name='Ibuprofeno',
                    description='Antiinflamatorio no esteroideo',
                    stock=80,
                    unit='tabletas'
                ),
                Medication(
                    name='Amoxicilina',
                    description='Antibiótico de amplio espectro',
                    stock=50,
                    unit='cápsulas'
                ),
                Medication(
                    name='Omeprazol',
                    description='Inhibidor de la bomba de protones',
                    stock=60,
                    unit='cápsulas'
                )
            ]
            db.session.add_all(medications)
            
            # Create sample patients
            patients = [
                Patient(
                    patient_id='P00001',
                    expediente='EXP00001',
                    name='Ana López',
                    email='ana.lopez@email.com',
                    phone='555-0201',
                    birth_date=datetime(1985, 5, 15),
                    blood_type='O+',
                    allergies='Ninguna'
                ),
                Patient(
                    patient_id='P00002',
                    expediente='EXP00002',
                    name='Roberto Martínez',
                    email='roberto.martinez@email.com',
                    phone='555-0202',
                    birth_date=datetime(1990, 8, 22),
                    blood_type='A+',
                    allergies='Penicilina'
                )
            ]
            db.session.add_all(patients)
            
            db.session.commit()
            
            # Create sample appointments (after committing patients and doctors)
            appointments = [
                Appointment(
                    patient_id=1,
                    doctor_id=1,
                    date=datetime.now().date(),
                    time=datetime.now().time(),
                    reason='Consulta de rutina'
                ),
                Appointment(
                    patient_id=2,
                    doctor_id=2,
                    date=datetime.now().date() + timedelta(days=1),
                    time=datetime.now().time(),
                    reason='Control mensual'
                )
            ]
            db.session.add_all(appointments)
            db.session.commit()
            
            print('Base de datos inicializada con datos de ejemplo')
        except Exception as e:
            db.session.rollback()
            print(f'Error al inicializar la base de datos: {e}')

if __name__ == '__main__':
    port = int(os.environ.get('PORT', 8000))
    with app.app_context():
        db.create_all()
        # Only initialize database if it's empty
        if not User.query.first():
            init_db()
    app.run(host='0.0.0.0', port=port)
