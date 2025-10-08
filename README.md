# Medical Appointment Booking Website

A full-stack web application that allows patients to book medical appointments with doctors. Built using **Django** for the backend and **HTML, CSS, and JavaScript** for the frontend, this project provides an intuitive interface for users to view available slots, book appointments, and manage them via a dashboard.

---

## Features

- **User Registration & Login:** Secure registration and login system for patients.
- **Book Appointments:** Users can select a department, view available slots for a particular day, and book appointments.
- **Automatic Slot Management:** The system shows available, full, or closed slots for each day.
- **Patient Dashboard:** View all upcoming and past appointments with details including doctor, department, and symptoms.
- **Departments & Doctors:** Automatic assignment of doctors based on the selected department.
- **Responsive Design:** Optimized for desktop and mobile screens.
- **Custom Styling:** Clean, modern interface using HTML, CSS, and JavaScript.

---

## Tech Stack

- **Backend:** Django (Python)
- **Frontend:** HTML, CSS, JavaScript
- **Database:** SQLite (default for Django; can switch to PostgreSQL/MySQL)
- **Version Control:** Git & GitHub

---

## Installation Guide

1. **Clone the repository**
   ```bash
   git clone https://github.com/harshith-ngit/medical-appoinment-booking-.git
   cd medical-appoinment-booking-

2. **Create a virtual environment**
    ```bash
    python -m venv venv

3. **Activate the virtual environment**
    Windows
    ```bash
    venv\Scripts\activate

    Linux / MacOS
    ```bash
    source venv/bin/activate

4. **Install dependencies**
    ```bash
    pip install -r requirements.txt

5. **Apply database migrations**
    ```bash
    python manage.py migrate

6. **Run the development server**
    ```bash
    python manage.py runserver

7. **Open in browser**
    ```bash
    http://127.0.0.1:8000/



