# Chemical Equipment Visualizer (Hybrid Web + Desktop)

A full-stack hybrid application for analyzing and visualizing chemical equipment data. This project demonstrates a unified system where a single **Django Backend** serves data to both a **React Web Client** and a **PyQt5 Desktop Client**, ensuring real-time synchronization and data parity across platforms.

## Architecture

- **Backend:** Django + Django REST Framework (DRF)
  - Handles data parsing (Pandas), storage (SQLite), and authentication.
  - Exposes RESTful endpoints for upload, history, and stats.
- **Web Client:** React.js + Chart.js + Bootstrap
  - Responsive Single Page Application (SPA).
  - Features glassmorphism UI, dynamic charts, and JWT-ready structure.
- **Desktop Client:** Python (PyQt5) + Matplotlib
  - Native GUI application.
  - Replicates full web functionality including Login, Charts, and PDF downloads.

---

## Features

1.  **Universal Authentication:**
    - Secure Login & Signup (Basic Auth).
    - User-specific data isolation (Users see only their own history).
2.  **Data Processing:**
    - Upload CSV files containing chemical parameter data.
    - Automatic calculation of Summary Stats (Avg Flowrate, Pressure, Temperature).
3.  **Visualization:**
    - Interactive Bar Charts showing Equipment Type distribution.
    - Data Tables for raw entry inspection.
4.  **History Management:**
    - Tracks last 5 uploads per user.
    - Persistent history across Web and Desktop (Upload on one, view on other).
5.  **Reporting:**
    - One-click PDF Report generation and download.

---

## Installation & Setup

### Prerequisites
- Python 3.8+
- Node.js & npm

### 1. Backend Setup (Django)
```bash
cd backend
# Create virtual environment
python -m venv venv
# Activate: Windows -> venv\Scriptsctivate | Mac/Linux -> source venv/bin/activate

# Install dependencies
pip install django djangorestframework pandas django-cors-headers reportlab

# Initialize Database
python manage.py makemigrations
python manage.py migrate

# Create Admin User (Optional)
python manage.py createsuperuser

# Run Server
python manage.py runserver
```
*Server running at: `http://127.0.0.1:8000/`*

### 2. Web Client Setup (React)
```bash
cd web_client
# Install dependencies
npm install axios chart.js react-chartjs-2 bootstrap

# Start Application
npm start
```
*App running at: `http://localhost:3000/`*

### 3. Desktop Client Setup (PyQt5)
```bash
cd desktop_client
# Install dependencies
pip install requests PyQt5 matplotlib

# Run Application
python main.py
```

---

## Project Structure
```text
/ChemicalVisualizer
├── backend/                 # Django Project
│   ├── api/                 # App logic (Views, Models, Serializers)
│   ├── core/                # Settings & URLs
│   └── manage.py
├── web_client/              # React Project
│   ├── src/                 # App.js, index.css, Components
│   └── public/
└── desktop_client/          # PyQt5 Project
    └── main.py              # Desktop Entry Point
```

## Sample Data
Use the provided `sample_equipment_data.csv` or generated test files to verify functionality.
**Columns Required:** `Equipment Name`, `Type`, `Flowrate`, `Pressure`, `Temperature`

## Demo Highlights
- **Cross-Platform Sync:** Upload on Web -> Instant appearance in Desktop History.
- **Secure Access:** Private user sessions protected by authentication.
- **Data Export:** Professional PDF reports generated server-side.

---
**Author:** Alisha Ahmad
