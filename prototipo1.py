import cv2
import mediapipe as mp
import math

# Inicializar MediaPipe Pose
mp_pose = mp.solutions.pose
mp_drawing = mp.solutions.drawing_utils

pose = mp_pose.Pose(
    static_image_mode=False,
    model_complexity=1,
    enable_segmentation=False,
    min_detection_confidence=0.7,
    min_tracking_confidence=0.7
)

# Función para calcular ángulo entre 3 puntos
def calcular_angulo(a, b, c):
    angulo = math.degrees(
        math.atan2(c[1] - b[1], c[0] - b[0]) -
        math.atan2(a[1] - b[1], a[0] - b[0])
    )
    angulo = abs(angulo)
    if angulo > 180:
        angulo = 360 - angulo
    return angulo

# Iniciar cámara
cap = cv2.VideoCapture(0)

while cap.isOpened():
    ret, frame = cap.read()
    if not ret:
        break

    frame = cv2.flip(frame, 1)
    rgb = cv2.cvtColor(frame, cv2.COLOR_BGR2RGB)
    results = pose.process(rgb)

    if results.pose_landmarks:
        # Obtener landmarks del brazo derecho (por ejemplo)
        landmarks = results.pose_landmarks.landmark

        hombro = [landmarks[mp_pose.PoseLandmark.RIGHT_SHOULDER.value].x * frame.shape[1],
                   landmarks[mp_pose.PoseLandmark.RIGHT_SHOULDER.value].y * frame.shape[0]]
        codo = [landmarks[mp_pose.PoseLandmark.RIGHT_ELBOW.value].x * frame.shape[1],
                landmarks[mp_pose.PoseLandmark.RIGHT_ELBOW.value].y * frame.shape[0]]
        muñeca = [landmarks[mp_pose.PoseLandmark.RIGHT_WRIST.value].x * frame.shape[1],
                  landmarks[mp_pose.PoseLandmark.RIGHT_WRIST.value].y * frame.shape[0]]

        # Calcular ángulo en el codo
        angulo_codo = calcular_angulo(hombro, codo, muñeca)

        # Dibujar
        cv2.circle(frame, tuple(map(int, hombro)), 8, (255, 0, 0), -1)
        cv2.circle(frame, tuple(map(int, codo)), 8, (0, 255, 0), -1)
        cv2.circle(frame, tuple(map(int, muñeca)), 8, (0, 0, 255), -1)
        cv2.line(frame, tuple(map(int, hombro)), tuple(map(int, codo)), (255, 255, 255), 2)
        cv2.line(frame, tuple(map(int, codo)), tuple(map(int, muñeca)), (255, 255, 255), 2)

        # Mostrar ángulo
        cv2.putText(frame, f'Angulo: {int(angulo_codo)} deg', 
                    (50, 50), cv2.FONT_HERSHEY_SIMPLEX, 
                    1, (0, 255, 255), 2, cv2.LINE_AA)

    cv2.imshow('RehabTech - Deteccion de Brazo', frame)

    if cv2.waitKey(1) & 0xFF == 27:  # Presiona ESC para salir
        break

cap.release()
cv2.destroyAllWindows()
