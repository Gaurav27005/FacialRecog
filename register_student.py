import cv2, os, time, re, numpy as np

DATASET_DIR = "dataset"
IMAGES_TO_CAPTURE = 7
CAPTURE_INTERVAL = 2.0
BRIGHTNESS_THRESHOLD = 80 

def clean_input(text):
    text = text.strip().replace(" ", "-").replace("_", "-")
    return re.sub(r'[^A-Za-z0-9\-]', '', text)

def start_capture(grade, div, roll, name):
    grade = clean_input(grade)
    div = clean_input(div)
    roll = clean_input(roll)
    name = clean_input(name)
    
    if not name or not grade:
        print("[ERROR] Missing details. Capture cancelled.")
        return

    folder_name = f"{grade}_{div}_{roll}_{name}"
    student_dir = os.path.join(DATASET_DIR, folder_name)
    if not os.path.exists(student_dir): os.makedirs(student_dir)

    print(f"\n[INFO] Starting Mac camera for {name}...")
    cam = cv2.VideoCapture(0)
    
    cam.set(cv2.CAP_PROP_FRAME_WIDTH, 640) 
    cam.set(cv2.CAP_PROP_FRAME_HEIGHT, 480)
    cam.set(cv2.CAP_PROP_FPS, 30)           
    cam.set(cv2.CAP_PROP_BUFFERSIZE, 1)     
    
    time.sleep(1)
    
    is_capturing = False
    captured_count = 0
    last_capture_time = 0

    while True:
        ret, frame = cam.read()
        if not ret: break
        
        frame = cv2.flip(frame, 1)
        display_frame = frame.copy()

        if not is_capturing:
            gray = cv2.cvtColor(frame, cv2.COLOR_BGR2GRAY)
            can_start = np.mean(gray) >= BRIGHTNESS_THRESHOLD
            
            cv2.putText(display_frame, f"Student: {name}", (20, 40), cv2.FONT_HERSHEY_SIMPLEX, 1.0, (255, 255, 255), 2)
            if can_start:
                cv2.putText(display_frame, "Press SPACE to Start", (20, 80), cv2.FONT_HERSHEY_SIMPLEX, 0.8, (0, 255, 0), 2)
            else:
                cv2.putText(display_frame, "Too Dark!", (20, 80), cv2.FONT_HERSHEY_SIMPLEX, 0.8, (0, 0, 255), 2)
            
            cv2.imshow("Registration", display_frame)
            key = cv2.waitKey(50)  
            if key == 32 and can_start:
                is_capturing = True
                last_capture_time = time.time() - CAPTURE_INTERVAL
            elif key == ord('q'): break
        else:
            time_remaining = CAPTURE_INTERVAL - (time.time() - last_capture_time)
            if time_remaining <= 0:
                cv2.imwrite(os.path.join(student_dir, f"{folder_name}_{captured_count}.jpg"), cv2.flip(frame, 1))
                captured_count += 1
                last_capture_time = time.time()
                print(f"✅ Captured {captured_count}/{IMAGES_TO_CAPTURE}")
            
            cv2.putText(display_frame, f"Capturing: {captured_count}/{IMAGES_TO_CAPTURE}", (20, 40), cv2.FONT_HERSHEY_SIMPLEX, 1.0, (0, 255, 255), 2)
            cv2.imshow("Registration", display_frame)
            cv2.waitKey(50)  
            
            if captured_count >= IMAGES_TO_CAPTURE:
                print(f"[SUCCESS] Registration complete for {name}!")
                break

    cam.release()
    cv2.destroyAllWindows()