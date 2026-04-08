# Attendance Management System using Face Recognition

Cloud-ready Face Recognition Attendance Management System built with Django, OpenCV, and Bootstrap 5.

## Features
- secure role-based login (Admin/Staff)
- Real-time webcam face capture directly from the browser natively (Cloud ready).
- Face encoding extraction utilizing `face_recognition` library.
- Dashboard with detailed metrics and Chart.js visualizations.
- Automatic anti-duplicate daily attendance tracking.
- CSV Reports Export.
- REST framework APIs.

## Requirements
- Python 3.9+ (Python 3.12 recommended)
- Django 6.x
- dlib, face_recognition, opencv-python

> **Note for Windows users:** You may need to install [Visual Studio Build Tools](https://visualstudio.microsoft.com/visual-cpp-build-tools/) with "Desktop development with C++" and CMake selected, before installing the requirements so that `dlib` can compile successfully.

## Installation Steps
### 1. Clone & Navigate to the Project
```bash
cd Attendance-using-face-recognition
```

### 2. Create the Virtual Environment
**For Linux/macOS:**
```bash
python3 -m venv venv
```
**For Windows:**
```cmd
python -m venv venv
```

### 3. Activate the Virtual Environment
**For Linux/macOS:**
```bash
source venv/bin/activate
```
**For Windows:**
```cmd
venv\Scripts\activate
```
*(If you encounter a script execution error on Windows, run PowerShell as Admin and execute `Set-ExecutionPolicy Unrestricted`)*

### 4. Install Dependencies
```bash
pip install -r requirements.txt
```

### 5. Apply Database Migrations
```bash
python manage.py migrate
```

### 6. Admin Credentials
A default superuser has been created (if the database is pre-populated):
- **Username:** admin
- **Password:** admin123

*(If you need to create a new one, run `python manage.py createsuperuser`)*

## Running the Application
To start the local server, make sure your virtual environment is activated, then run:

**For Linux/macOS:**
```bash
python3 manage.py runserver
```
**For Windows:**
```cmd
python manage.py runserver
```

Visit http://127.0.0.1:8000 in your web browser.

## How to use
1. Log in.
2. Go to **Students** -> **Add New Student**. Upload a photo showing a clear face. Saving the student will compute the face encoding in background.
3. Once the face is encoded successfully (Status: Yes), go to **Live Attendance**.
4. Click **Start** to open your webcam. The system will capture a frame every 2 seconds, checking against the database, and automatically log attendance if a match is found.
5. Go to **Attendance Logs** or **Dashboard** to export CSV reports.
