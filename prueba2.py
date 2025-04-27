import cv2
import mediapipe as mp

mp_hands = mp.solutions.hands
mp_drawing = mp.solutions.drawing_utils

# Iniciar cámara
cap = cv2.VideoCapture(0)

with mp_hands.Hands(
    max_num_hands=2,  # Solo una mano para simplificar
    min_detection_confidence=0.7,
    min_tracking_confidence=0.7
) as hands:

    while cap.isOpened():
        ret, frame = cap.read()
        if not ret:
            break

        frame = cv2.flip(frame, 1)
        rgb = cv2.cvtColor(frame, cv2.COLOR_BGR2RGB)
        results = hands.process(rgb)

        if results.multi_hand_landmarks:
            for idx, hand_landmarks in enumerate(results.multi_hand_landmarks):
                # Dibuja la mano
                mp_drawing.draw_landmarks(frame, hand_landmarks, mp_hands.HAND_CONNECTIONS)
                
                hand_label = results.multi_handedness[idx].classification[0].label

                # Lógica de dedos levantados
                dedos = 0
                # Índice
                if hand_landmarks.landmark[mp_hands.HandLandmark.INDEX_FINGER_TIP].y < \
                   hand_landmarks.landmark[mp_hands.HandLandmark.INDEX_FINGER_PIP].y:
                    dedos += 1
                # Medio
                if hand_landmarks.landmark[mp_hands.HandLandmark.MIDDLE_FINGER_TIP].y < \
                   hand_landmarks.landmark[mp_hands.HandLandmark.MIDDLE_FINGER_PIP].y:
                    dedos += 1
                # Anular
                if hand_landmarks.landmark[mp_hands.HandLandmark.RING_FINGER_TIP].y < \
                   hand_landmarks.landmark[mp_hands.HandLandmark.RING_FINGER_PIP].y:
                    dedos += 1
                # Meñique
                if hand_landmarks.landmark[mp_hands.HandLandmark.PINKY_TIP].y < \
                   hand_landmarks.landmark[mp_hands.HandLandmark.PINKY_PIP].y:
                    dedos += 1
                if hand_label == "Right":        
                    # Pulgar (se compara en X porque se mueve de lado)
                    if hand_landmarks.landmark[mp_hands.HandLandmark.THUMB_TIP].x > \
                    hand_landmarks.landmark[mp_hands.HandLandmark.THUMB_IP].x:
                        dedos += 1
                else:  # pulgar izquierdo
                    if hand_landmarks.landmark[mp_hands.HandLandmark.THUMB_TIP].x < \
                       hand_landmarks.landmark[mp_hands.HandLandmark.THUMB_IP].x:
                        dedos += 1
                """ #--- PRUEBA PARA DOS MANOS ---
                
                if hand_landmarks.landmark[mp_hands.HandLandmark.INDEX_FINGER_TIP].y < 
                   hand_landmarks.landmark[mp_hands.HandLandmark.INDEX_FINGER_PIP].y:
                    dedos1 += 1
                # Medio
                if hand_landmarks.landmark[mp_hands.HandLandmark.MIDDLE_FINGER_TIP].y < 
                   hand_landmarks.landmark[mp_hands.HandLandmark.MIDDLE_FINGER_PIP].y:
                    dedos1 += 1
                # Anular
                if hand_landmarks.landmark[mp_hands.HandLandmark.RING_FINGER_TIP].y < 
                   hand_landmarks.landmark[mp_hands.HandLandmark.RING_FINGER_PIP].y:
                    dedos1 += 1
                # Meñique
                if hand_landmarks.landmark[mp_hands.HandLandmark.PINKY_TIP].y < 
                   hand_landmarks.landmark[mp_hands.HandLandmark.PINKY_PIP].y:
                    dedos1 += 1
                # Pulgar (se compara en X porque se mueve de lado)
                if hand_landmarks.landmark[mp_hands.HandLandmark.THUMB_TIP].x > 
                   hand_landmarks.landmark[mp_hands.HandLandmark.THUMB_IP].x:
                    dedos1 += 1 """

                # Mostrar número
                texto = f"{hand_label} hand: {dedos} dedos"
                cv2.putText(frame, texto, (10, 50 + idx * 40),
                            cv2.FONT_HERSHEY_SIMPLEX, 1, (0, 255, 0), 2)

        cv2.imshow("Contador de Dedos", frame)
        if cv2.waitKey(1) & 0xFF == 27:
            break

cap.release()
cv2.destroyAllWindows()
