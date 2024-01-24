from pythonfiles import db,session
from sqlalchemy.orm import sessionmaker
from sqlalchemy import create_engine, Column, Integer, String, ForeignKey, DateTime, Date,Time, Enum
from sqlalchemy.orm import relationship
from datetime import datetime
from sqlalchemy import Float




class Patient(db.Model):
    __tablename__ = 'patients'
    patient_id = Column(Integer, primary_key=True, autoincrement=True)
    patient_number = Column(String(20), unique=True, nullable=False)
    patient_name = Column(String(50))
    age = Column(Integer)
    address = Column(String(100))
    admit_date = Column(DateTime, default=datetime.utcnow)
    discharge_date = Column(DateTime, nullable=True)  
    remaining_fees = Column(Float, default=0.0)
    room_id = Column(Integer, ForeignKey('rooms.room_id'))
    room = relationship("Room", back_populates="patients")
    relatives = relationship("Relative", back_populates="patient")




class Relative(db.Model):
    __tablename__ = 'relatives'
    relative_id = Column(Integer, primary_key=True, autoincrement=True)
    patient_id = Column(Integer, ForeignKey('patients.patient_id'), nullable=False)
    relative_name = Column(String(50))
    relative_contact_number = Column(String(20))
    patient = relationship("Patient", back_populates="relatives")




class Doctor(db.Model):
    __tablename__ = 'doctors'
    doctor_id = Column(Integer, primary_key=True, autoincrement=True)
    name = Column(String(50))
    email = Column(String(50), unique=True, nullable=False)
    contact_number = Column(String(20), nullable=False)
    specialization = Column(String(50))
    cabin_number = Column(String(20))
    password = Column(String(200), nullable=False)
    fees = Column(Float)
    appointments = relationship("Appointment", back_populates="doctor")



class Appointment(db.Model):
    __tablename__ = 'appointments'
    appointment_id = Column(Integer, primary_key=True, autoincrement=True)
    doctor_id = Column(Integer, ForeignKey('doctors.doctor_id'))
    # patient_id = Column(Integer, ForeignKey('patients.patient_id'))  # Add this line
    appointment_date = Column(Date)
    status = Column(Enum('Scheduled', 'Cancelled', 'Completed'))
    patient_number = Column(Integer, unique=True, nullable=False)
    fees = Column(Integer)
    doctor = relationship("Doctor", back_populates="appointments")
    patient_name = Column(String(50))
    # patient = relationship("Patient", back_populates="appointments")




class Room(db.Model):
    __tablename__ = 'rooms'
    room_id = Column(Integer, primary_key=True, autoincrement=True)
    floor = Column(Integer)
    room_number = Column(Integer)
    max_patients = Column(Integer, default=4)
    patients = relationship("Patient", back_populates="room")




class Staff(db.Model):
    __tablename__ = 'staff'
    staff_id = Column(Integer, primary_key=True, autoincrement=True)
    email = Column(String(50), unique=True, nullable=False)
    name = Column(String(50))
    contact_number = Column(String(20), unique=True, nullable=False)
    designation = Column(String(50))
    password = Column(String(200), nullable=False)


