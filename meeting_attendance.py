import time, pickle, numpy as np, pandas as pd, mss, os, cv2
import pyautogui
from datetime import datetime

# --- CONFIGURATION ---
pyautogui.FAILSAFE = False 
DATABASE_FILE = "student_encodings.pkl"
TOLERANCE = 0.42 
TOTAL_PAGES = 3
NEXT_PAGE_BUTTON_X, NEXT_PAGE_BUTTON_Y = 1850, 500

# --- THE STOPWATCH FIX ---
# Lowered to 5 seconds to provide highly accurate Join/Leave timestamps 
TEST_SLEEP_SECONDS = 5 
FLAG_FILE = "monitor.run"

attendance_tracker = {}
total_scans_performed = 0

def export_attendance(is_backup=False):
    global attendance_tracker, total_scans_performed
    if not attendance_tracker or total_scans_performed == 0: return
    
    data = []
    for rid, info in attendance_tracker.items():
        count = info.get("Times Detected", 0)
        perc = (count / total_scans_performed) * 100
        
        # --- LIVENESS REPORTING LOGIC ---
        if info.get("Is_Spoofing", False):
            status = "SPOOF DETECTED"
            perc = 0 # Revoke attendance
        elif perc >= 75: status = "Present"
        elif perc >= 30: status = "Partial"
        else: status = "Absent"
        
        data.append({
            "Div": info["Div"], 
            "Roll No": info["Roll No"], 
            "Name": info["Name"],
            "Join Time": info["Join_Time"],     
            "Leave Time": info["Leave_Time"],   
            "Times Detected": count, 
            "Attendance %": f"{int(perc)}%", 
            "Status": status
        })

    df = pd.DataFrame(data).sort_values(by=['Div', 'Roll No'])
    filename = "Attendance_Live_Backup.xlsx" if is_backup else f"Attendance_Final_{datetime.now().strftime('%H-%M')}.xlsx"
    df.to_excel(filename, index=False)
    if not is_backup: print(f"\n✅ FINAL SUCCESS: Saved as {filename}\n")

def run_monitor():
    global total_scans_performed, attendance_tracker
    
    # Isolate AI memory block for Apple Silicon
    import face_recognition 
    
    if not os.path.exists(DATABASE_FILE): 
        print("[ERROR] Database not found!")
        return
        
    with open(DATABASE_FILE, "rb") as f:
        db = pickle.load(f)
        known_enc, known_meta = db["encodings"], db["metadata"]

    # Initialize Liveness & Time Tracking variables
    for meta in known_meta: 
        attendance_tracker[meta["Raw_ID"]] = {
            **meta, 
            "Times Detected": 0,
            "Static_Strikes": 0,    
            "Anchor_Enc": None,     
            "Anchor_Box_Area": 0,   # Locks in their physical 3D distance
            "Is_Spoofing": False,
            "Join_Time": "N/A",
            "Leave_Time": "N/A"
        }
    
    sct = mss.mss()
    print(f"[INFO] Monitor Started. Scanning for {len(known_meta)} known faces.")
    
    try:
        while os.path.exists(FLAG_FILE):
            for i in range(TEST_SLEEP_SECONDS, 0, -1):
                if not os.path.exists(FLAG_FILE): break
                print(f"STATUS: Next scan in: {i}s", flush=True)
                time.sleep(1)
            
            if not os.path.exists(FLAG_FILE): break
            
            total_scans_performed += 1
            print(f"STATUS: ⚠️ SCANNING PAGE 1...", flush=True)
            print(f"\n--- Scan #{total_scans_performed} Started ---")
            
            seen_this_round = set()
            now = datetime.now().strftime('%H:%M:%S') 
            
            for page in range(TOTAL_PAGES):
                if not os.path.exists(FLAG_FILE): break
                print(f"STATUS: Scanning Page {page+1}/{TOTAL_PAGES}...", flush=True)
                
                try:
                    sct_img = sct.grab(sct.monitors[1])
                    img = np.array(sct_img)
                    small = cv2.resize(img, (0,0), fx=0.5, fy=0.5)
                    rgb = cv2.cvtColor(small, cv2.COLOR_BGRA2RGB)
                    
                    # Strict 8-bit memory allocation to prevent Mac dlib crashes
                    strict_rgb = np.ascontiguousarray(rgb, dtype=np.uint8)
                    
                    locs = face_recognition.face_locations(strict_rgb, model="hog")
                    encs = face_recognition.face_encodings(strict_rgb, locs, model="large")
                    
                    for (t, r, b, l), e in zip(locs, encs):
                        dist = face_recognition.face_distance(known_enc, e)
                        if len(dist) > 0 and np.min(dist) <= TOLERANCE:
                            rid = known_meta[np.argmin(dist)]["Raw_ID"]
                            
                            # Calculate the pixel area of the face box (Width * Height)
                            current_area = (b - t) * (r - l)
                            
                            # --- ULTRA-STRICT 2D/3D LIVENESS DETECTION ---
                            if attendance_tracker[rid]["Anchor_Enc"] is not None:
                                anchor_dist = face_recognition.face_distance([attendance_tracker[rid]["Anchor_Enc"]], e)[0]
                                anchor_area = attendance_tracker[rid]["Anchor_Box_Area"]
                                area_variance = abs(current_area - anchor_area) / anchor_area if anchor_area > 0 else 1.0
                                
                                # TRAP: To pass, you MUST change your facial expression by > 12% 
                                # AND your body depth/posture must change by > 4%.
                                if anchor_dist < 0.12 or area_variance < 0.04:
                                    attendance_tracker[rid]["Static_Strikes"] += 1
                                    print(f"  [WARNING] {rid} spoof detected! Dist: {anchor_dist:.3f}, Depth: {area_variance:.3f} (Strike {attendance_tracker[rid]['Static_Strikes']})")
                                else:
                                    # Genuine human movement detected. Forgive 1 strike and reset the Anchors.
                                    attendance_tracker[rid]["Static_Strikes"] = max(0, attendance_tracker[rid]["Static_Strikes"] - 1)
                                    attendance_tracker[rid]["Anchor_Enc"] = e 
                                    attendance_tracker[rid]["Anchor_Box_Area"] = current_area
                            else:
                                # First time seeing them, lock in the Anchors
                                attendance_tracker[rid]["Anchor_Enc"] = e
                                attendance_tracker[rid]["Anchor_Box_Area"] = current_area
                            
                            # STRICT: Only 3 strikes allowed (15 seconds of being still)
                            if attendance_tracker[rid]["Static_Strikes"] >= 3:
                                attendance_tracker[rid]["Is_Spoofing"] = True
                            
                            # --- TIME TRACKING & ATTENDANCE ---
                            if not attendance_tracker[rid]["Is_Spoofing"]:
                                if attendance_tracker[rid]["Join_Time"] == "N/A":
                                    attendance_tracker[rid]["Join_Time"] = now
                                attendance_tracker[rid]["Leave_Time"] = now
                                seen_this_round.add(rid)
                                
                except Exception as e: 
                    print(f"[ERROR] Screen grab failed: {e}")

                if page < TOTAL_PAGES - 1 and os.path.exists(FLAG_FILE):
                    pyautogui.moveTo(NEXT_PAGE_BUTTON_X, NEXT_PAGE_BUTTON_Y)
                    pyautogui.click()
                    time.sleep(3) 
            
            for rid in seen_this_round: attendance_tracker[rid]["Times Detected"] += 1
            print(f"Scan #{total_scans_performed} Done. Unique Faces: {len(seen_this_round)}")
            export_attendance(is_backup=True)
            
    except Exception as e: 
        print(f"Critical Error: {e}")
    finally: 
        export_attendance(is_backup=False)

if __name__ == "__main__":
    run_monitor()