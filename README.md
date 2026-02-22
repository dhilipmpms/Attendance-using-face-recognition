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
- Python 3.9+
- Django 6.x
- dlib, face_recognition, opencv-python
- create a virtual environment 
## Installation Steps
1. Navigate to the project directory:
   ```bash
   cd Attendance-using-face-recognition
   ```
2. Activate the virtual environment:
   ```bash
   source venv/bin/activate
   ```
3. *(If not already installed)* Install the python packages:
   ```bash
   pip install -r requirements.txt
   pip install setuptools
   ```
4. Run migrations:
   ```bash
   python manage.py migrate
   ```
5. A default superuser has been created with:
   - **Username:** admin
   - **Password:** admin123
   *(If not present, you can create one with `python manage.py createsuperuser`)*

## Running the Application
To run the local server, execute:
```bash
python manage.py runserver
```
Visit http://127.0.0.1:8000 in your web browser.

## How to use
1. Log in.
2. Go to **Students** -> **Add New Student**. Upload a photo showing a clear face. Saving the student will compute the face encoding in background.
3. Once the face is encoded successfully (Status: Yes), go to **Live Attendance**.
4. Click **Start** to open your webcam. The system will capture a frame every 2 seconds, checking against the database, and automatically log attendance if a match is found.
5. Go to **Attendance Logs** or **Dashboard** to export CSV reports.
