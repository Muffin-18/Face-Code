# face_emotion_module.py

import cv2
from deepface import DeepFace
from collections import deque
import threading
import time


class EmotionDetector:

    def __init__(self, camera_index=0):

        self.cap = cv2.VideoCapture(camera_index)

        self.emotion_window = deque(maxlen=10)
        self.current_confidence = 0
        self.current_emotion = "neutral"
        self.latest_frame = None

        self.lock = threading.Lock()
        self.running = True

        self.thread = threading.Thread(target=self._process, daemon=True)
        self.thread.start()

    def _map_emotion(self, emotion):

        positive = {"happy", "surprise"}
        negative = {"sad", "fear", "angry", "disgust"}

        if emotion in positive:
            return "confident"
        elif emotion in negative:
            return "struggling"
        return "neutral"

    def _process(self):

        frame_count = 0

        while self.running:
            ret, frame = self.cap.read()
            if not ret:
                time.sleep(0.05)
                continue

            frame_count += 1

            if frame_count % 20 == 0:
                try:
                    result = DeepFace.analyze(
                        frame,
                        actions=["emotion"],
                        enforce_detection=False
                    )

                    dominant = result[0]["dominant_emotion"]
                    confidence = result[0]["emotion"][dominant]

                    mapped = self._map_emotion(dominant)

                    with self.lock:
                        self.emotion_window.append(mapped)
                        self.current_confidence = confidence

                        if len(self.emotion_window) > 0:
                            self.current_emotion = max(
                                set(self.emotion_window),
                                key=self.emotion_window.count
                            )

                except:
                    pass

            with self.lock:
                display = frame.copy()
                cv2.putText(
                    display,
                    f"{self.current_emotion}",
                    (10, 30),
                    cv2.FONT_HERSHEY_SIMPLEX,
                    0.8,
                    (0, 255, 0),
                    2
                )
                self.latest_frame = display

            time.sleep(0.02)

    def get_emotion_state(self):
        with self.lock:
            return self.current_emotion, self.current_confidence

    def get_latest_frame(self):
        with self.lock:
            return self.latest_frame

    def stop(self):
        self.running = False
        if self.cap.isOpened():
            self.cap.release()