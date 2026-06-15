import os, pickle, numpy as np, cv2

DATASET_PATH, DATABASE_FILE = "dataset", "student_encodings.pkl"

def build_database():
    import face_recognition 
    
    print("\n--- 🧠 HIGH-ACCURACY DATABASE BUILDER ---")
    if not os.path.exists(DATASET_PATH): 
        print("[ERROR] Dataset folder not found!")
        return
        
    known_encodings, known_metadata = [], []

    for student_folder in os.listdir(DATASET_PATH):
        if student_folder.startswith('.'): continue
        
        folder_path = os.path.join(DATASET_PATH, student_folder)
        if not os.path.isdir(folder_path): continue
        parts = student_folder.split('_')
        
        folder_encs = []
        print(f"Deep-learning facial structure for: {student_folder}...", end=" ", flush=True)
        for filename in os.listdir(folder_path):
            if filename.startswith('.'): continue
            
            if filename.lower().endswith(('.jpg', '.png', '.jpeg')):
                img_path = os.path.join(folder_path, filename)
                try:
                    img = cv2.imread(img_path)
                    if img is None: continue
                    
                    rgb = cv2.cvtColor(img, cv2.COLOR_BGR2RGB)
                    strict_rgb = np.ascontiguousarray(rgb, dtype=np.uint8)
                    
                    encs = face_recognition.face_encodings(strict_rgb, num_jitters=5, model="large")
                    if encs: folder_encs.append(encs[0])
                    
                except Exception as e:
                    print(f"\n[WARNING] Skipping {filename} due to error: {e}")

        if folder_encs:
            known_encodings.append(np.mean(folder_encs, axis=0))
            known_metadata.append({
                "Grade": parts[0], "Div": parts[1], "Roll No": parts[2], 
                "Name": "_".join(parts[3:]), "Raw_ID": student_folder
            })
            print("DONE ✅")
        else:
            print("FAILED ❌ (No faces found)")

    with open(DATABASE_FILE, "wb") as f:
        pickle.dump({"encodings": known_encodings, "metadata": known_metadata}, f)
    print(f"\n[SUCCESS] AI trained with {len(known_encodings)} students!")

if __name__ == "__main__":
    build_database()