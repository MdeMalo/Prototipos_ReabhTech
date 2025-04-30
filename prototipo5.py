import cv2
import mediapipe as mp
import math
import json
from datetime import datetime
import matplotlib.pyplot as plt
import numpy as np
import os
import tkinter as tk
from PIL import Image, ImageTk
from matplotlib.backends.backend_tkagg import FigureCanvasTkAgg
import winsound

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

# Preparar datos para JSON
base_dir = "rehabtech_data"
os.makedirs(base_dir, exist_ok=True)
nombre_archivo = os.path.join(base_dir, f"rehabtech_data_{datetime.now().strftime('%Y%m%d_%H%M%S')}.json")
datos = []

# Iniciar cámara
cap = cv2.VideoCapture(0)
if not cap.isOpened():
    print("Error: No se pudo abrir la cámara")
    exit()

# Obtener la resolución nativa del video
frame_width = int(cap.get(cv2.CAP_PROP_FRAME_WIDTH))
frame_height = int(cap.get(cv2.CAP_PROP_FRAME_HEIGHT))

# Crear ventana Tkinter
root = tk.Tk()
root.title("RehabTech - Ejercicios de Brazo")
root.state("zoomed")  # Configurar la ventana en pantalla completa

# Frame principal para dividir la ventana
main_frame = tk.Frame(root)
main_frame.pack(fill=tk.BOTH, expand=True, padx=10, pady=10)

# Frame izquierdo para video y título
left_frame = tk.Frame(main_frame)
left_frame.pack(side=tk.LEFT, fill=tk.BOTH, expand=True)

# Título "Ejercicios de estiramiento"
title_label = tk.Label(left_frame, text="Ejercicios de estiramiento", font=("Arial", 14, "bold"), bg="white", pady=5)
title_label.pack(fill=tk.X)

# Frame para el video
video_frame = tk.Frame(left_frame, bd=2, relief=tk.SUNKEN)
video_frame.pack(fill=tk.BOTH, expand=True, pady=5)

# Label para mostrar el video
video_label = tk.Label(video_frame)
video_label.pack(fill=tk.BOTH, expand=True)

# Frame derecho para detalles y gráfico
right_frame = tk.Frame(main_frame, bd=2, relief=tk.RAISED, width=450)  # Aumentar el ancho a 450 píxeles
right_frame.pack(side=tk.RIGHT, fill=tk.Y, padx=10)
right_frame.pack_propagate(False)  # Evitar que el frame derecho se redimensione

# Título "Detalles"
details_label = tk.Label(right_frame, text="Detalles", font=("Arial", 14, "bold"))
details_label.pack(fill=tk.X)

# Frame para el mensaje
message_frame = tk.Frame(right_frame, bd=2, relief=tk.SUNKEN, bg="white")
message_frame.pack(fill=tk.X, pady=5)

# Mensaje "Ajusta la posición de tu codo"
message_label = tk.Label(message_frame, text="Mensaje:\nAjusta la posición de tu codo", font=("Arial", 12), bg="white", justify=tk.LEFT)
message_label.pack(padx=10, pady=10, anchor=tk.W)

# Configurar gráfico Matplotlib
fig, ax = plt.subplots(figsize=(6, 4))  # Aumentar el tamaño de la gráfica
x_data = []
y_data_der = []
y_data_izq = []
linea_der, = ax.plot(x_data, y_data_der, 'b-', label="Ángulo Codo Derecho")
linea_izq, = ax.plot(x_data, y_data_izq, 'r-', label="Ángulo Codo Izquierdo")
ax.set_ylim(0, 200)
ax.set_xlabel('Frames')
ax.set_ylabel('Ángulo (°)')
ax.set_title('Seguimiento de Ángulo de Brazos')
ax.legend()

# Incrustar gráfico en Tkinter
canvas = FigureCanvasTkAgg(fig, master=right_frame)
canvas.draw()
canvas.get_tk_widget().pack(fill=tk.BOTH, expand=True, pady=10)

# Frame inferior para botones
bottom_frame = tk.Frame(root)
bottom_frame.pack(fill=tk.X, pady=5)

# Botón "Cerrar"
close_button = tk.Button(bottom_frame, text="Cerrar", font=("Arial", 12), bg="#FF4040", fg="white", command=lambda: on_closing())
close_button.pack(side=tk.LEFT, padx=10)

# Frame para los botones de iconos (Chat, Pose, Audio)
icons_frame = tk.Frame(bottom_frame)
icons_frame.pack(side=tk.RIGHT, padx=10)

# Botones simulando los iconos
chat_button = tk.Button(icons_frame, text="Chat", font=("Arial", 10))
chat_button.pack(side=tk.LEFT, padx=5)
pose_button = tk.Button(icons_frame, text="Pose", font=("Arial", 10))
pose_button.pack(side=tk.LEFT, padx=5)
audio_button = tk.Button(icons_frame, text="Audio", font=("Arial", 10))
audio_button.pack(side=tk.LEFT, padx=5)

# Función para actualizar video y gráfico
def update_frame():
    global frame_count, contador_der, contador_izq, estado_der, estado_izq
    
    ret, frame = cap.read()
    if not ret:
        root.quit()
        return

    frame = cv2.flip(frame, 1)
    rgb = cv2.cvtColor(frame, cv2.COLOR_BGR2RGB)
    results = pose.process(rgb)

    if results.pose_landmarks:
        mp_drawing.draw_landmarks(
            frame,
            results.pose_landmarks,
            mp_pose.POSE_CONNECTIONS,
            mp_drawing.DrawingSpec(color=(0, 255, 0), thickness=2, circle_radius=4),
            mp_drawing.DrawingSpec(color=(255, 0, 0), thickness=2)
        )

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

        # BRAZO IZQUIERDO
        hombro_izq = [landmarks[mp_pose.PoseLandmark.LEFT_SHOULDER.value].x * frame.shape[1],
                      landmarks[mp_pose.PoseLandmark.LEFT_SHOULDER.value].y * frame.shape[0]]
        codo_izq = [landmarks[mp_pose.PoseLandmark.LEFT_ELBOW.value].x * frame.shape[1],
                    landmarks[mp_pose.PoseLandmark.LEFT_ELBOW.value].y * frame.shape[0]]
        muñeca_izq = [landmarks[mp_pose.PoseLandmark.LEFT_WRIST.value].x * frame.shape[1],
                      landmarks[mp_pose.PoseLandmark.LEFT_WRIST.value].y * frame.shape[0]]

        angulo_codo_izq = calcular_angulo(hombro_izq, codo_izq, muñeca_izq)
        angulos_izq.append(angulo_codo_izq)

        # Actualizar gráfico
        frame_count += 1
        x_data.append(frame_count)
        y_data_der.append(angulo_codo_der)
        y_data_izq.append(angulo_codo_izq)
        linea_der.set_xdata(x_data)
        linea_der.set_ydata(y_data_der)
        linea_izq.set_xdata(x_data)
        linea_izq.set_ydata(y_data_izq)
        ax.set_xlim(max(0, frame_count-100), frame_count + 10)
        canvas.draw()

        # Contar repeticiones brazo derecho
        if angulo_codo_der > 160:
            estado_der = "bajando"
        if angulo_codo_der < 30 and estado_der == "bajando":
            contador_der += 1
            estado_der = "subiendo"
            winsound.Beep(1000, 200)

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

        estado_texto_der = estado_der if estado_der is not None else "Sin movimiento"
        cv2.putText(frame, f'Der Estado: {estado_texto_der}', 
                    (30, 130), cv2.FONT_HERSHEY_SIMPLEX, 
                    0.8, (255, 255, 255), 2, cv2.LINE_AA)

        # Contar repeticiones brazo izquierdo
        if angulo_codo_izq > 160:
            estado_izq = "bajando"
        if angulo_codo_izq < 30 and estado_izq == "bajando":
            contador_izq += 1
            estado_izq = "subiendo"

        estado_texto_izq = estado_izq if estado_izq is not None else "Sin movimiento"
        cv2.putText(frame, f'Izq Estado: {estado_texto_izq}', 
                    (30, 170), cv2.FONT_HERSHEY_SIMPLEX, 
                    0.8, (255, 255, 255), 2, cv2.LINE_AA)

        # Mostrar contador
        cv2.putText(frame, f'Reps Der: {contador_der}', (400, 50),
                    cv2.FONT_HERSHEY_SIMPLEX, 1, (255, 0, 0), 2)
        cv2.putText(frame, f'Reps Izq: {contador_izq}', (400, 130),
                    cv2.FONT_HERSHEY_SIMPLEX, 1, (0, 0, 255), 2)

    # Convertir frame para Tkinter
    frame_rgb = cv2.cvtColor(frame, cv2.COLOR_BGR2RGB)
    img = Image.fromarray(frame_rgb)
    
    # Escalar el tamaño de la imagen para mostrarla más grande sin cambiar la resolución
    scale_factor = 1.5  # Aumentar el tamaño en un 50%
    new_width = int(frame_width * scale_factor)
    new_height = int(frame_height * scale_factor)
    img = img.resize((new_width, new_height), Image.Resampling.LANCZOS)
    
    imgtk = ImageTk.PhotoImage(image=img)
    video_label.imgtk = imgtk  # Guardar referencia
    video_label.configure(image=imgtk)

    # Programar próxima actualización
    root.after(10, update_frame)

# Función para cerrar la aplicación
def on_closing():
    # Guardar datos al final
    promedio_der = sum(angulos_der) / len(angulos_der) if angulos_der else 0
    promedio_izq = sum(angulos_izq) / len(angulos_izq) if angulos_izq else 0
    entrada = {
        "fecha": datetime.now().strftime("%Y-%m-%d %H:%M:%S"),
        "repeticiones_derecho": contador_der,
        "repeticiones_izquierdo": contador_izq,
        "promedio_angulo_derecho": round(promedio_der, 2),
        "promedio_angulo_izquierdo": round(promedio_izq, 2)
    }
    datos.append(entrada)
    with open(nombre_archivo, mode='w') as file:
        json.dump(datos, file, indent=4)
    
    cap.release()
    root.destroy()

# Configurar cierre de ventana
root.protocol("WM_DELETE_WINDOW", on_closing)

# Iniciar actualización
update_frame()

# Iniciar bucle principal de Tkinter
root.mainloop()