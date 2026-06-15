Here is the updated markdown text with the author name adjusted. You can copy and paste this directly into your GitHub repository's `README.md` file.

```markdown
# AI Facial Recognition Attendance System

An advanced, automated attendance tracking system powered by AI facial recognition. This application is specifically designed to seamlessly monitor student attendance during online meetings (capable of detecting faces in online meeting grids at random intervals) or in-person classes, complete with anti-spoofing features and automated Excel report generation.

## 🌟 Features

* **Interactive GUI Dashboard:** Built with `customtkinter` for a sleek, modern, and user-friendly dark-mode interface.
* **Smart Student Registration:** Captures training images via webcam with built-in brightness checks and an interactive capture sequence.
* **High-Accuracy Database Builder:** Uses the `face_recognition` library and Deep Learning models (HOG/CNN) to build precise facial encodings.
* **Live Camera Verification:** A dedicated testing module to verify student identification in real-time before starting the monitor.
* **Automated Screen Monitoring:** Automatically scans virtual meeting screens (e.g., Zoom, Google Meet) in the background. It even auto-clicks to paginate through multi-page participant grids.
* **Advanced Liveness Detection:** Includes ultra-strict 2D/3D liveness detection. By measuring facial expression variations and depth/posture changes (bounding box area), it catches static photo spoofing attempts.
* **Automated Excel Reporting:** Tracks Join Time, Leave Time, total times detected, attendance percentages, and generates a formatted Excel file marking students as "Present", "Partial", "Absent", or "SPOOF DETECTED".

## 📁 Project Structure

```text
├── attendance_app.py        # Main GUI Application Dashboard
├── register_student.py      # Webcam capture module for new students
├── build_database.py        # Extracts facial encodings and builds student_encodings.pkl
├── meeting_attendance.py    # Background screen scanner and Excel exporter
├── test_recognition.py      # Real-time webcam testing module
├── dataset/                 # Directory where raw student images are stored
├── student_encodings.pkl    # Serialized database of known faces (Generated)
└── monitor.run              # Temporary flag file for background processes

```

## 🛠️ Prerequisites & Installation

1. **Python 3.8+** is recommended.
2. Ensure you have a working webcam and a C++ compiler installed (required for building `dlib`, which is a dependency for `face_recognition`).
3. Install the required Python packages:

```bash
pip install opencv-python numpy pandas face_recognition mss pyautogui customtkinter openpyxl

```

*(Note: If you are on Mac/Apple Silicon, ensure your environment is set up to compile `dlib` correctly, as the code includes strict memory allocation to prevent Mac `dlib` crashes).*

## 🚀 How to Use

### 1. Launch the Application

Start the main dashboard by running:

```bash
python attendance_app.py

```

### 2. Register Students

* Click **"📸 Register Student"**.
* Enter the student's details (Grade, Division, Roll No, Name).
* A webcam window will open. Ensure the room is well-lit (the system has a brightness threshold).
* Press **SPACE** to begin capturing. The system will automatically take 7 photos at fixed intervals.

### 3. Build the Database

* Once all students are registered, click **"🧠 Build Database"**.
* The system will process all images in the `dataset` folder, extract facial features, and save them to `student_encodings.pkl`. Watch the system logs on the dashboard for progress.

### 4. Test Camera (Optional)

* Click **"🧪 Test Camera"** to verify that the AI successfully recognizes registered faces in real-time. Press `q` to exit the test window.

### 5. Start Monitoring (For Virtual Meetings)

* Open your virtual meeting (Zoom, Teams, etc.) on your secondary monitor.
* Click **"▶ Start Monitor"**.
* The script will continuously take screenshots, detect faces, enforce liveness checks, and record presence.

### 6. Stop and Export

* When the class/meeting is over, click **"⏹ Stop & Save Excel"**.
* A final Excel sheet (e.g., `Attendance_Final_HH-MM.xlsx`) will be generated in your project directory containing the detailed attendance report.

## ⚙️ Configuration & Tweaks

You may need to modify a few variables in `meeting_attendance.py` to match your specific screen setup and meeting software:

* `TOTAL_PAGES`: Number of participant pages the monitor should scan through (Default: 3).
* `NEXT_PAGE_BUTTON_X, NEXT_PAGE_BUTTON_Y`: The `(X, Y)` screen coordinates for the "Next Page" button in your meeting software. You **must** adjust `(1850, 500)` to match your monitor's resolution.
* `sct.monitors[1]`: The `mss` screen grabber looks at monitor `1`. Change this index if your meeting window is on a different display.
* `TOLERANCE`: The facial recognition distance tolerance (Default: `0.42`). Lower values make it stricter, higher values make it more lenient.

## 👤 Author

**Gaurav Thorat**

```

```
