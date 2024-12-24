import cv2
import os
import numpy as np
import glob
import csv

class FaceRegistration:
    def __init__(self):
        self.face_classifier = cv2.CascadeClassifier('haarcascade_frontalface_default.xml')

    def save_csv(self, user_info, filename="user_info.csv"):
        """사용자 정보를 CSV 파일에 저장"""
        file_exists = os.path.exists(filename)
        with open(filename, "a", newline="", encoding="utf-8") as csvfile:
            fieldnames = [
                "아이디", "이름", "생년월일", "성별", "연락처", "주소", "키", "몸무게", "운동량"
            ]
            writer = csv.DictWriter(csvfile, fieldnames=fieldnames)
            if not file_exists:
                writer.writeheader()
            writer.writerow(user_info)

    def face_extractor(self, img):
        if img is None:
            print("Error: Input image is None")
            return None
        gray = cv2.cvtColor(img, cv2.COLOR_BGR2GRAY)
        faces = self.face_classifier.detectMultiScale(gray, 1.3, 5)
        if len(faces) == 0:
            return None
        return [img[y:y+h, x:x+w] for (x, y, w, h) in faces]

    def generate_folder(self, base_path):
        i = 1
        while True:
            folder_name = f"sesac{i:02d}"
            folder_path = os.path.join(base_path, folder_name)
            if not os.path.exists(folder_path):
                return folder_name, folder_path
            i += 1

    def save_faces(self, faces, save_path, user_id, count):
        for idx, face in enumerate(faces):
            face_resized = cv2.resize(face, (200, 200))
            face_gray = cv2.cvtColor(face_resized, cv2.COLOR_BGR2GRAY)
            file_name = os.path.join(save_path, f"{user_id}_{count + idx}.jpg")
            cv2.imwrite(file_name, face_gray)

    def train_model(self, train_path):
        Training_Data, Labels = [], []
        image_paths = glob.glob(os.path.join(train_path, "*.jpg"))

        for i, image_path in enumerate(image_paths):
            images = cv2.imread(image_path, cv2.IMREAD_GRAYSCALE)
            Training_Data.append(np.asarray(images, dtype=np.uint8))
            Labels.append(i)

        Labels = np.asarray(Labels, dtype=np.int32)
        model = cv2.face.LBPHFaceRecognizer_create()
        model.train(np.asarray(Training_Data), np.asarray(Labels))
        model.save(os.path.join(train_path, "trained_model.yml"))
