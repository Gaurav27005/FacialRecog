import customtkinter as ctk
import threading, sys, os
import multiprocessing
import subprocess
import register_student

ctk.set_appearance_mode("dark")  
ctk.set_default_color_theme("blue")  

class RegistrationPopup(ctk.CTkToplevel):
    def __init__(self, parent):
        super().__init__(parent)
        self.title("Enter Student Details")
        self.geometry("300x350")
        
        self.attributes("-topmost", True)  
        self.focus_force()                 
        self.grab_set()                    
        
        ctk.CTkLabel(self, text="New Student Registration", font=("Arial", 16, "bold")).pack(pady=10)
        
        self.grade = self.create_input("Grade (e.g. BE)")
        self.div = self.create_input("Division (e.g. A)")
        self.roll = self.create_input("Roll No (e.g. 21)")
        self.name = self.create_input("Name (e.g. Atharva)")
        
        ctk.CTkButton(self, text="Start Camera", fg_color="#2ecc71", command=self.submit).pack(pady=20)

    def create_input(self, placeholder):
        entry = ctk.CTkEntry(self, placeholder_text=placeholder)
        entry.pack(pady=5, padx=20, fill="x")
        return entry

    def submit(self):
        g, d, r, n = self.grade.get(), self.div.get(), self.roll.get(), self.name.get()
        if g and d and r and n:
            self.destroy() 
            multiprocessing.Process(target=register_student.start_capture, args=(g, d, r, n), daemon=True).start()

class App(ctk.CTk):
    def __init__(self):
        super().__init__()
        self.title("Pro Attendance Monitor")
        self.geometry("600x700")
        
        self.label = ctk.CTkLabel(self, text="AI Attendance Dashboard", font=("Arial", 24, "bold"))
        self.label.pack(pady=(20, 5))
        
        self.status_label = ctk.CTkLabel(self, text="Status: Ready", font=("Consolas", 16), text_color="#f1c40f")
        self.status_label.pack(pady=(0, 15))

        self.btn_frame = ctk.CTkFrame(self, fg_color="transparent")
        self.btn_frame.pack(pady=10)

        ctk.CTkButton(self.btn_frame, text="📸 Register Student", fg_color="#2ecc71", width=180, height=40,
                      command=self.open_registration).grid(row=0, column=0, padx=10, pady=10)
                      
        ctk.CTkButton(self.btn_frame, text="🧠 Build Database", fg_color="#3498db", width=180, height=40,
                      command=self.run_build_db).grid(row=0, column=1, padx=10, pady=10)
        
        ctk.CTkButton(self.btn_frame, text="🧪 Test Camera", fg_color="#f1c40f", width=180, height=40,
                      command=self.run_test_cam).grid(row=1, column=0, padx=10, pady=10)
        
        self.start_btn = ctk.CTkButton(self.btn_frame, text="▶ Start Monitor", fg_color="#e74c3c", width=180, height=40, command=self.start_monitor)
        self.start_btn.grid(row=1, column=1, padx=10, pady=10)

        self.stop_btn = ctk.CTkButton(self, text="⏹ Stop & Save Excel", fg_color="#555555", width=380, height=40, state="disabled", command=self.stop_monitor)
        self.stop_btn.pack(pady=10)

        ctk.CTkLabel(self, text="System Logs:", font=("Arial", 14, "bold")).pack(anchor="w", padx=40)
        self.log_box = ctk.CTkTextbox(self, width=520, height=200, state="disabled", fg_color="#111111")
        self.log_box.pack(pady=(0, 20))

        sys.stdout = TextRedirector(self.log_box)

    def open_registration(self):
        RegistrationPopup(self)

    def run_build_db(self):
        def worker():
            print("\n[INFO] Launching Database Builder...")
            process = subprocess.Popen([sys.executable, "build_database.py"], stdout=subprocess.PIPE, stderr=subprocess.STDOUT, text=True)
            for line in process.stdout: print(line, end="")
        threading.Thread(target=worker, daemon=True).start()

    def run_test_cam(self):
        def worker():
            print("\n[INFO] Launching Camera Test...")
            subprocess.run([sys.executable, "test_recognition.py"])
        threading.Thread(target=worker, daemon=True).start()

    def start_monitor(self):
        self.start_btn.configure(state="disabled")
        self.stop_btn.configure(state="normal", fg_color="#e67e22")
        
        with open("monitor.run", "w") as f: f.write("running")
        
        def worker():
            print("\n[INFO] Launching Background Screen Scanner...")
            process = subprocess.Popen(
                [sys.executable, "meeting_attendance.py"], 
                stdout=subprocess.PIPE, 
                stderr=subprocess.STDOUT, 
                text=True, bufsize=1
            )
            for line in process.stdout:
                if line.startswith("STATUS:"):
                    status_text = line.replace("STATUS:", "").strip()
                    self.after(0, lambda t=status_text: self.status_label.configure(text=f"Status: {t}"))
                else:
                    print(line, end="")
                    
            self.after(0, lambda: self.status_label.configure(text="Status: Stopped"))
                    
        threading.Thread(target=worker, daemon=True).start()

    def stop_monitor(self):
        print("\n[INFO] Stopping scanner and exporting Excel...")
        self.start_btn.configure(state="normal")
        self.stop_btn.configure(state="disabled", fg_color="#555555")
        
        if os.path.exists("monitor.run"):
            os.remove("monitor.run")
        self.status_label.configure(text="Status: Saving Final Excel...")

class TextRedirector:
    def __init__(self, widget): 
        self.widget = widget
        
    def write(self, str_text):
        self.widget.after(0, lambda: self._safe_write(str_text))
        
    def _safe_write(self, str_text):
        self.widget.configure(state="normal")
        self.widget.insert("end", str_text)
        self.widget.see("end")
        self.widget.configure(state="disabled")
        
    def flush(self): 
        pass

if __name__ == "__main__":
    multiprocessing.freeze_support() 
    if os.path.exists("monitor.run"): os.remove("monitor.run")
    app = App()
    app.mainloop()