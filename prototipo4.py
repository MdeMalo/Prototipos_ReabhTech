import cv2
import mediapipe as mp
import math
import csv
from datetime import datetime
import matplotlib.pyplot as plt
import numpy as np

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

# Variables
contador_der = 0
contador_izq = 0
estado_der = None
estado_izq = None
angulos_der = []
angulos_izq = []
frame_count = 0

# Crear archivo CSV
nombre_archivo = f"rehabtech_data_{datetime.now().strftime('%Y%m%d_%H%M%S')}.csv"
with open(nombre_archivo, mode='w', newline='') as file:
    writer = csv.writer(file)
    writer.writerow(["Fecha", "Repeticiones Derecho", "Repeticiones Izquierdo", "Promedio Ángulo Derecho", "Promedio Ángulo Izquierdo"])

# Iniciar cámara
cap = cv2.VideoCapture(0)

# Configurar gráfico en vivo
plt.ion()
fig, ax = plt.subplots()
x_data = []
y_data = []
linea, = ax.plot(x_data, y_data, label="Ángulo Codo Derecho")
ax.set_ylim(0, 200)
ax.set_xlabel('Frames')
ax.set_ylabel('Ángulo (°)')
ax.set_title('Seguimiento de Ángulo de Brazo (Derecho)')
ax.legend()

while cap.isOpened():
    ret, frame = cap.read()
    if not ret:
        break

    frame = cv2.flip(frame, 1)
    rgb = cv2.cvtColor(frame, cv2.COLOR_BGR2RGB)
    results = pose.process(rgb)

    if results.pose_landmarks:
        landmarks = results.pose_landmarks.landmark

        # BRAZO DERECHO
        hombro_der = [landmarks[mp_pose.PoseLandmark.RIGHT_SHOULDER.value].x * frame.shape[1],
                      landmarks[mp_pose.PoseLandmark.RIGHT_SHOULDER.value].y * frame.shape[0]]
        codo_der = [landmarks[mp_pose.PoseLandmark.RIGHT_ELBOW.value].x * frame.shape[1],
                    landmarks[mp_pose.PoseLandmark.RIGHT_ELBOW.value].y * frame.shape[0]]
        muñeca_der = [landmarks[mp_pose.PoseLandmark.RIGHT_WRIST.value].x * frame.shape[1],
                      landmarks[mp_pose.PoseLandmark.RIGHT_WRIST.value].y * frame.shape[0]]
        
        angulo_codo_der = calcular_angulo(hombro_der, codo_der, muñeca_der)
        angulos_der.append(angulo_codo_der)

        # Actualizar gráfico
        frame_count += 1
        x_data.append(frame_count)
        y_data.append(angulo_codo_der)
        linea.set_xdata(x_data)
        linea.set_ydata(y_data)
        ax.set_xlim(max(0, frame_count-100), frame_count + 10)  # Mostrar solo últimos 100 frames
        plt.draw()
        plt.pause(0.001)

        # Contar repeticiones brazo derecho
        if angulo_codo_der > 160:
            estado_der = "bajando"
        if angulo_codo_der < 30 and estado_der == "bajando":
            contador_der += 1
            estado_der = "subiendo"

        # Mostrar datos en pantalla
        cv2.putText(frame, f'Der: {int(angulo_codo_der)} deg', 
                    (30, 50), cv2.FONT_HERSHEY_SIMPLEX, 
                    0.8, (0, 255, 255), 2, cv2.LINE_AA)

        if 30 < angulo_codo_der < 160:
            cv2.putText(frame, "Der: Movimiento OK", (30, 90),
                        cv2.FONT_HERSHEY_SIMPLEX, 0.8, (0, 255, 0), 2)
        else:
            cv2.putText(frame, "Der: Corrige!", (30, 90),
                        cv2.FONT_HERSHEY_SIMPLEX, 0.8, (0, 0, 255), 2)

        # --- También para brazo izquierdo (puedes usar igual que el derecho)
        hombro_izq = [landmarks[mp_pose.PoseLandmark.LEFT_SHOULDER.value].x * frame.shape[1],
                      landmarks[mp_pose.PoseLandmark.LEFT_SHOULDER.value].y * frame.shape[0]]
        codo_izq = [landmarks[mp_pose.PoseLandmark.LEFT_ELBOW.value].x * frame.shape[1],
                    landmarks[mp_pose.PoseLandmark.LEFT_ELBOW.value].y * frame.shape[0]]
        muñeca_izq = [landmarks[mp_pose.PoseLandmark.LEFT_WRIST.value].x * frame.shape[1],
                      landmarks[mp_pose.PoseLandmark.LEFT_WRIST.value].y * frame.shape[0]]

        angulo_codo_izq = calcular_angulo(hombro_izq, codo_izq, muñeca_izq)
        angulos_izq.append(angulo_codo_izq)

        if angulo_codo_izq > 160:
            estado_izq = "bajando"
        if angulo_codo_izq < 30 and estado_izq == "bajando":
            contador_izq += 1
            estado_izq = "subiendo"

    # Mostrar contador
    cv2.putText(frame, f'Reps Der: {contador_der}', (400, 50),
                cv2.FONT_HERSHEY_SIMPLEX, 1, (255, 0, 0), 2)
    cv2.putText(frame, f'Reps Izq: {contador_izq}', (400, 130),
                cv2.FONT_HERSHEY_SIMPLEX, 1, (0, 0, 255), 2)

    cv2.imshow('RehabTech - Ejercicios de Brazo + Grafica', frame)

    if cv2.waitKey(1) & 0xFF == 27:  # ESC
        break

# Guardar datos al final
promedio_der = sum(angulos_der) / len(angulos_der) if angulos_der else 0
promedio_izq = sum(angulos_izq) / len(angulos_izq) if angulos_izq else 0

with open(nombre_archivo, mode='a', newline='') as file:
    writer = csv.writer(file)
    writer.writerow([
        datetime.now().strftime("%Y-%m-%d %H:%M:%S"),
        contador_der,
        contador_izq,
        round(promedio_der, 2),
        round(promedio_izq, 2)
    ])

cap.release()
cv2.destroyAllWindows()
plt.ioff()
plt.show()