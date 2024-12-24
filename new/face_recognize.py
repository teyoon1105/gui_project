import cv2
import os
import pyttsx3


class FaceRecognition:
    def __init__(self, use_tts=True):
        # OpenCV의 HaarCascade를 사용하여 얼굴 검출
        self.face_classifier = cv2.CascadeClassifier('haarcascade_frontalface_default.xml')
        self.model = None
        self.use_tts = use_tts
        if use_tts:
            self.engine = pyttsx3.init()

    def face_detector(self, img):
        """이미지에서 얼굴 영역을 검출"""
        try:
            gray = cv2.cvtColor(img, cv2.COLOR_BGR2GRAY)
            faces = self.face_classifier.detectMultiScale(gray, 1.3, 5)

            # 얼굴이 검출되지 않으면 None 반환
            if len(faces) == 0:
                return None, img

            # 첫 번째 얼굴 영역만 반환
            for (x, y, w, h) in faces:
                roi = img[y:y + h, x:x + w]
            return roi, img
        except Exception as e:
            print(f"[Error] face_detector 실패: {e}")
            return None, img

    def load_model(self, model_path):
        """LBPHFaceRecognizer 모델을 로드"""
        print(f"Loading model from: {model_path}")
        if not os.path.exists(model_path):
            raise FileNotFoundError(f"Model not found at the specified path: {model_path}")

        try:
            self.model = cv2.face.LBPHFaceRecognizer_create()
            self.model.read(model_path)
            print("Model loaded successfully.")
        except Exception as e:
            raise RuntimeError(f"Failed to load the model: {e}")

    def recognize_faces(self, frame, user_data):
        face, annotated_frame = self.face_detector(frame)
        if face is not None:
            face = cv2.cvtColor(face, cv2.COLOR_BGR2GRAY)
            result = self.model.predict(face)
            confidence = int(100 * (1 - (result[1] / 300)))

            if confidence > 80:
                user_id = user_data[result[0]]["아이디"]
                user_name = user_data[result[0]]["이름"]
                cv2.putText(annotated_frame, f"{user_name} ({confidence:.2f}%)", (10, 50),
                            cv2.FONT_HERSHEY_SIMPLEX, 0.8, (0, 255, 0), 2)
                return f"{user_id}: {user_name}", annotated_frame
            else:
                cv2.putText(annotated_frame, "Unknown", (10, 50),
                            cv2.FONT_HERSHEY_SIMPLEX, 0.8, (0, 0, 255), 2)
                return "Unknown", annotated_frame
        return "No face detected", annotated_frame


    def start_recognition(self, user_name):
        """웹캠에서 얼굴 인식을 실행"""
        try:
            cap = cv2.VideoCapture(0)
            if not cap.isOpened():
                raise IOError("Cannot access the webcam.")

            while True:
                ret, frame = cap.read()
                if not ret:
                    print("[Warning] Failed to capture frame.")
                    continue

                message, image = self.recognize_faces(frame, user_name)

                # 메시지 출력
                cv2.putText(image, message, (20, 50), cv2.FONT_HERSHEY_SIMPLEX, 1, (0, 255, 0), 2)
                cv2.imshow("Face Recognition", image)

                # ESC 키를 누르면 종료
                if cv2.waitKey(1) & 0xFF == 27:
                    break

            cap.release()
            cv2.destroyAllWindows()

        except Exception as e:
            print(f"[Error] start_recognition 실패: {e}")
            raise RuntimeError(f"Failed to start recognition: {e}")
