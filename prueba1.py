import cv2
import mediapipe as mp

# Inicializa Holistic y Drawing
mp_drawing = mp.solutions.drawing_utils
mp_holistic = mp.solutions.holistic

# Abre la cámara
cap = cv2.VideoCapture(0)

with mp_holistic.Holistic(
        static_image_mode=False,
        model_complexity=1,
        smooth_landmarks=True,
        enable_segmentation=True,
        refine_face_landmarks=True,  # También desactivamos refinamiento facial
        min_detection_confidence=0.7,
        min_tracking_confidence=0.7) as holistic:

    while cap.isOpened():
        ret, frame = cap.read()
        if not ret:
            print("No se pudo acceder a la cámara.")
            break

        # Convierte BGR a RGB
        image = cv2.cvtColor(frame, cv2.COLOR_BGR2RGB)
        image.flags.writeable = False

        # Procesa con MediaPipe
        results = holistic.process(image)

        # Convierte RGB de nuevo a BGR
        image.flags.writeable = True
        image = cv2.cvtColor(image, cv2.COLOR_RGB2BGR)

        # Dibuja solo pose y manos (NO rostro)
        if results.left_hand_landmarks:
            mp_drawing.draw_landmarks(
                image, results.left_hand_landmarks, mp_holistic.HAND_CONNECTIONS)

        if results.right_hand_landmarks:
            mp_drawing.draw_landmarks(
                image, results.right_hand_landmarks, mp_holistic.HAND_CONNECTIONS)

        if results.pose_landmarks:
            mp_drawing.draw_landmarks(
                image, results.pose_landmarks, mp_holistic.POSE_CONNECTIONS)

        # Muestra el frame
        cv2.imshow('MediaPipe Holistic - sin rostro', image)

        if cv2.waitKey(5) & 0xFF == 27:  # Presiona ESC para salir
            break

cap.release()
cv2.destroyAllWindows()
