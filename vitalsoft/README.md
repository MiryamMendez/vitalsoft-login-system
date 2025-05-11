# VitalSoft Medical System

A simple medical system built with Flask, MySQL, HTML, Tailwind CSS, and JavaScript.

## Features

- Patient registration
- Appointment scheduling
- Viewing patient appointment records

## Setup Instructions

1. Install Python dependencies:
```
pip install flask flask-mysqldb
```

2. Setup MySQL database:

```sql
CREATE DATABASE vitalsoft;

USE vitalsoft;

CREATE TABLE patients (
    id INT AUTO_INCREMENT PRIMARY KEY,
    name VARCHAR(100) NOT NULL,
    email VARCHAR(100) NOT NULL
);

CREATE TABLE appointments (
    id INT AUTO_INCREMENT PRIMARY KEY,
    patient_id INT NOT NULL,
    date DATE NOT NULL,
    FOREIGN KEY (patient_id) REFERENCES patients(id)
);
```

3. Update MySQL credentials in `vitalsoft/app.py` if needed.

4. Run the Flask app:

```
python vitalsoft/app.py
```

5. Access the app at `http://localhost:5000`

## Notes

- This is a simple demo system for medical management.
- Tailwind CSS is included via CDN for styling.
