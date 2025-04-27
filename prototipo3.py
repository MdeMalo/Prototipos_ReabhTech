import cv2
import mediapipe as mp
import math
import csv
from datetime import datetime
import matplotlib.pyplot as plt
import numpy as np
import json
import winsound  # Para retroalimentación auditiva (solo en Windows)

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
    """Calcula el ángulo en grados entre tres puntos.
    Args:
        a (list): Coordenadas del primer punto [x, y].
        b (list): Coordenadas del punto central [x, y].
        c (list): Coordenadas del tercer punto [x, y].
    Returns:
        float: Ángulo en grados."""
    angulo = math.degrees(
        math.atan2(c[1] - b[1], c[0] - b[0]) -
        math.atan2(a[1] - b[1], a[0] - b[0])
    )
    angulo = abs(angulo)
    if angulo > 180:
        angulo = 360 - angulo
    return angulo

# Función para obtener puntos de landmarks
def obtener_puntos_landmarks(landmarks, frame_shape):
    """Extrae coordenadas de los landmarks relevantes.
    Args:
        landmarks: Lista de landmarks detectados por MediaPipe.
        frame_shape (tuple): Dimensiones del frame (alto, ancho).
    Returns:
        dict: Coordenadas de hombros, codos y muñecas para ambos lados."""
    puntos = {}
    for lado in ['der', 'izq']:
        hombro = getattr(mp_pose.PoseLandmark, f'{"RIGHT" if lado == "der" else "LEFT"}_SHOULDER').value
        codo = getattr(mp_pose.PoseLandmark, f'{"RIGHT" if lado == "der" else "LEFT"}_ELBOW').value
        muñeca = getattr(mp_pose.PoseLandmark, f'{"RIGHT" if lado == "der" else "LEFT"}_WRIST').value
        puntos[f'hombro_{lado}'] = [landmarks[hombro].x * frame_shape[1], landmarks[hombro].y * frame_shape[0]]
        puntos[f'codo_{lado}'] = [landmarks[codo].x * frame_shape[1], landmarks[codo].y * frame_shape[0]]
        puntos[f'muñeca_{lado}'] = [landmarks[muñeca].x * frame_shape[1], landmarks[muñeca].y * frame_shape[0]]
    return puntos

# Función para procesar repeticiones
def procesar_reps(angulo, estado, contador, umbral_bajo=30, umbral_alto=160):
    """Detecta repeticiones basadas en el ángulo y umbrales.
    Args:
        angulo (float): Ángulo actual del codo.
        estado (str): Estado actual ("bajando", "subiendo" o None).
        contador (int): Número de repeticiones.
        umbral_bajo (int): Ángulo mínimo para detectar repetición.
        umbral_alto (int): Ángulo máximo para iniciar repetición.
    Returns:
        tuple: Nuevo estado y contador actualizado."""
    if angulo > umbral_alto:
        estado = "bajando"
    elif angulo < umbral_bajo and estado == "bajando":
        contador += 1
        estado = "subiendo"
        winsound.Beep(1000, 200)  # Sonido al completar una repetición
    return estado, contador

# Función principal
def main():
    # Configurar cámara
    cap = cv2.VideoCapture(0)
    
    # Variables iniciales
    contador_der, contador_izq = 0, 0
    estado_der, estado_izq = None, None
    angulos_der, angulos_izq = [], []
    frame_count = 0
    
    # Configurar gráfico en vivo
    plt.ion()
    fig, ax = plt.subplots()
    x_data, y_data = [], []
    linea, = ax.plot(x_data, y_data, label="Ángulo Codo Derecho")
    ax.set_ylim(0, 200)
    ax.set_xlabel('Frames')
    ax.set_ylabel('Ángulo (°)')
    ax.set_title('Seguimiento de Ángulo de Brazo (Derecho)')
    ax.legend()
    
    # Crear archivo CSV
    nombre_archivo = f"rehabtech_data_{datetime.now().strftime('%Y%m%d_%H%M%S')}.csv"
    with open(nombre_archivo, mode='w', newline='') as file:
        writer = csv.writer(file)
        writer.writerow(["Fecha", "Repeticiones Derecho", "Repeticiones Izquierdo", 
                         "Promedio Ángulo Derecho", "Promedio Ángulo Izquierdo"])
    
    while cap.isOpened():
        ret, frame = cap.read()
        if not ret:
            break
        
        frame = cv2.flip(frame, 1)  # Espejo horizontal
        rgb = cv2.cvtColor(frame, cv2.COLOR_BGR2RGB)
        results = pose.process(rgb)
        
        if results.pose_landmarks:
            puntos = obtener_puntos_landmarks(results.pose_landmarks.landmark, frame.shape)
            
            # Calcular ángulos
            angulo_der = calcular_angulo(puntos['hombro_der'], puntos['codo_der'], puntos['muñeca_der'])
            angulo_izq = calcular_angulo(puntos['hombro_izq'], puntos['codo_izq'], puntos['muñeca_izq'])
            angulos_der.append(angulo_der)
            angulos_izq.append(angulo_izq)
            
            # Procesar repeticiones
            estado_der, contador_der = procesar_reps(angulo_der, estado_der, contador_der)
            estado_izq, contador_izq = procesar_reps(angulo_izq, estado_izq, contador_izq)
            
            # Actualizar gráfico en vivo
            frame_count += 1
            x_data.append(frame_count)
            y_data.append(angulo_der)
            if len(x_data) > 100:  # Limitar a 100 puntos para optimizar
                x_data.pop(0)
                y_data.pop(0)
            linea.set_xdata(x_data)
            linea.set_ydata(y_data)
            ax.set_xlim(max(0, frame_count-100), frame_count + 10)
            plt.draw()
            plt.pause(0.001)
            
            # Mostrar datos en pantalla
            cv2.putText(frame, f'Der: {int(angulo_der)} deg | Reps: {contador_der}', (30, 50),
                        cv2.FONT_HERSHEY_SIMPLEX, 0.8, (0, 255, 255), 2)
            cv2.putText(frame, f'Izq: {int(angulo_izq)} deg | Reps: {contador_izq}', (30, 90),
                        cv2.FONT_HERSHEY_SIMPLEX, 0.8, (255, 0, 0), 2)
            
            # Feedback visual
            if 30 < angulo_der < 160:
                cv2.putText(frame, "Der: Movimiento OK", (30, 130),
                            cv2.FONT_HERSHEY_SIMPLEX, 0.8, (0, 255, 0), 2)
            else:
                cv2.putText(frame, "Der: Corrige!", (30, 130),
                            cv2.FONT_HERSHEY_SIMPLEX, 0.8, (0, 0, 255), 2)
            
            if 30 < angulo_izq < 160:
                cv2.putText(frame, "Izq: Movimiento OK", (30, 170),
                            cv2.FONT_HERSHEY_SIMPLEX, 0.8, (0, 255, 0), 2)
            else:
                cv2.putText(frame, "Izq: Corrige!", (30, 170),
                            cv2.FONT_HERSHEY_SIMPLEX, 0.8, (0, 0, 255), 2)
        
        cv2.imshow('RehabTech - Ejercicios de Brazo + Grafica', frame)
        
        if cv2.waitKey(1) & 0xFF == 27:  # Salir con tecla ESC
            break
    
    # Calcular promedios
    promedio_der = sum(angulos_der) / len(angulos_der) if angulos_der else 0
    promedio_izq = sum(angulos_izq) / len(angulos_izq) if angulos_izq else 0
    
    # Guardar datos en CSV
    with open(nombre_archivo, mode='a', newline='') as file:
        writer = csv.writer(file)
        writer.writerow([
            datetime.now().strftime("%Y-%m-%d %H:%M:%S"),
            contador_der,
            contador_izq,
            round(promedio_der, 2),
            round(promedio_izq, 2)
        ])
    
    # Guardar en JSON
    datos = {
        'reps_der': contador_der,
        'reps_izq': contador_izq,
        'prom_der': round(promedio_der, 2),
        'prom_izq': round(promedio_izq, 2)
    }
    with open(f"datos_{datetime.now().strftime('%Y%m%d_%H%M%S')}.json", 'w') as f:
        json.dump(datos, f)
    
    # Mostrar resumen en consola
    print(f"Resumen:\nReps Der: {contador_der}\nReps Izq: {contador_izq}\n"
          f"Promedio Der: {promedio_der:.2f}\nPromedio Izq: {promedio_izq:.2f}")
    
    # Liberar recursos
    cap.release()
    cv2.destroyAllWindows()
    plt.ioff()
    plt.show()

if __name__ == "__main__":
    main()