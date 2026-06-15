import cv2, pickle, numpy as np
import time, os

def test():
    import face_recognition

    if not os.path.exists("student_encodings.pkl"):
        print("\n[🚨 ERROR] student_encodings.pkl NOT FOUND!")
        return
        
    try:
        with open("student_encodings.pkl", "rb") as f:
            db = pickle.load(f)
            known_enc, known_meta = db["encodings"], db["metadata"]
    except Exception as e: 
        print(f"\n[🚨 ERROR] Could not read database: {e}\n")
        return
        
    print("\n[INFO] Starting Mac camera for verification...")
    cam = cv2.VideoCapture(0)
    
    cam.set(cv2.CAP_PROP_FRAME_WIDTH, 640)  
    cam.set(cv2.CAP_PROP_FRAME_HEIGHT, 480)
    cam.set(cv2.CAP_PROP_FPS, 30)           
    cam.set(cv2.CAP_PROP_BUFFERSIZE, 1)  
    
    time.sleep(1) 
    
    while True:
        ret, frame = cam.read()
        if not ret or frame is None or frame.size == 0: 
            continue
            
        frame = cv2.flip(frame, 1)
        resized = cv2.resize(frame, (0,0), fx=0.5, fy=0.5)
        
        rgb = cv2.cvtColor(resized, cv2.COLOR_BGR2RGB)
        rgb = np.ascontiguousarray(rgb, dtype=np.uint8)
        
        try:
            locs = face_recognition.face_locations(rgb)
            encs = face_recognition.face_encodings(rgb, locs, model="large")
            
            for (t, r, b, l), e in zip(locs, encs):
                dist = face_recognition.face_distance(known_enc, e)
                name = "Unknown"
                if len(dist) > 0 and np.min(dist) <= 0.42:
                    name = known_meta[np.argmin(dist)]['Name']
                    
                cv2.rectangle(frame, (l*2, t*2), (r*2, b*2), (0,255,0), 2)
                cv2.putText(frame, name, (l*2, t*2-10), cv2.FONT_HERSHEY_SIMPLEX, 0.7, (0,255,0), 2)
                
        except:
            pass
            
        cv2.imshow('Verification Test (Press Q to exit)', frame)
        
        if cv2.waitKey(10) & 0xFF == ord('q'): 
            break
            
    cam.release()
    cv2.destroyAllWindows()

if __name__ == "__main__":
    test()