import cv2
import mediapipe as mp
import pyautogui
import numpy as np
import time

# Inicialización de la cámara y FaceMesh
cam = cv2.VideoCapture(0)
face_mesh = mp.solutions.face_mesh.FaceMesh(refine_landmarks=True, min_detection_confidence=0.5, min_tracking_confidence=0.5)
screen_w, screen_h = pyautogui.size()

# Parámetros de control
speed = 10  # Controla la velocidad del cursor
num_points = 16  # Número de puntos fijos alrededor de la nariz
radius_factor = 0.1  # Factor del radio para los puntos alrededor de la nariz
fixed_points = []  # Lista para almacenar los puntos fijos
calibration_frames = 30  # Número de frames para calibrar
calibrated = False
calibration_center = None
recalibration_threshold = 100  # Distancia para recalibrar

# Parámetros de parpadeo
blink_threshold = 0.15  # Umbral de la relación de aspecto del ojo para considerar un parpadeo
short_blink_duration_threshold = 0.20  # Duración mínima para considerar un parpadeo corto (en segundos)
long_blink_duration_threshold = 0.5  # Duración mínima para considerar un parpadeo largo (en segundos)
drag_blink_duration_threshold = 1.0  # Duración mínima para considerar el inicio de arrastre (en segundos)
blink_start_time = None
blinking = False
dragging = False
click_timestamps = []  # Tiempos de los últimos clics para detectar doble clic

# Funciones de ayuda
def generate_fixed_points(center_x, center_y, radius, num_points):
    """Genera puntos fijos alrededor de un centro dado."""
    points = []
    angle_step = 2 * np.pi / num_points
    for i in range(num_points):
        angle = angle_step * i
        x = int(center_x + radius * np.cos(angle))
        y = int(center_y + radius * np.sin(angle))
        points.append((x, y))
    return points

def get_closest_point(nose, points):
    """Encuentra el punto en la circunferencia más cercano a la nariz."""
    closest_point = None
    min_distance = float('inf')
    for point in points:
        distance = np.linalg.norm(np.array(nose) - np.array(point))
        if distance < min_distance:
            min_distance = distance
            closest_point = point
    return closest_point, min_distance

def recalibrate(nose_x, nose_y, frame_w):
    """Recalibra los puntos fijos basados en la nueva posición de la nariz."""
    global fixed_points, calibration_center
    calibration_center = (nose_x, nose_y)
    fixed_points = generate_fixed_points(nose_x, nose_y, int(frame_w * radius_factor), num_points)
    print("Recalibración completada:", calibration_center)

def calculate_eye_aspect_ratio(landmarks, frame_w, frame_h):
    """Calcula la relación de aspecto del ojo basada en puntos faciales."""
    # Puntos específicos del ojo izquierdo
    left_eye_top = landmarks[159]
    left_eye_bottom = landmarks[145]
    left_eye_left = landmarks[130]
    left_eye_right = landmarks[243]

    # Puntos específicos del ojo derecho
    right_eye_top = landmarks[386]
    right_eye_bottom = landmarks[374]
    right_eye_left = landmarks[362]
    right_eye_right = landmarks[398]

    # Calcula distancias para el ojo izquierdo
    left_vert_dist = np.linalg.norm(np.array([left_eye_top.x * frame_w, left_eye_top.y * frame_h]) - np.array([left_eye_bottom.x * frame_w, left_eye_bottom.y * frame_h]))
    left_hori_dist = np.linalg.norm(np.array([left_eye_left.x * frame_w, left_eye_left.y * frame_h]) - np.array([left_eye_right.x * frame_w, left_eye_right.y * frame_h]))

    # Calcula distancias para el ojo derecho
    right_vert_dist = np.linalg.norm(np.array([right_eye_top.x * frame_w, right_eye_top.y * frame_h]) - np.array([right_eye_bottom.x * frame_w, right_eye_bottom.y * frame_h]))
    right_hori_dist = np.linalg.norm(np.array([right_eye_left.x * frame_w, right_eye_left.y * frame_h]) - np.array([right_eye_right.x * frame_w, right_eye_right.y * frame_h]))

    # Relación de aspecto del ojo
    left_ear = left_vert_dist / left_hori_dist if left_hori_dist != 0 else 0
    right_ear = right_vert_dist / right_hori_dist if right_hori_dist != 0 else 0

    # Usar el mínimo EAR de ambos ojos para mayor robustez
    return min(left_ear, right_ear)

def handle_blinks(ear):
    """Maneja los eventos de parpadeo para clics y arrastres."""
    global blink_start_time, blinking, dragging, click_timestamps

    current_time = time.time()

    if ear < blink_threshold:  # Ojos cerrados
        if not blinking:
            blinking = True
            blink_start_time = current_time
    else:  # Ojos abiertos
        if blinking:
            blink_duration = current_time - blink_start_time
            if blink_duration < short_blink_duration_threshold:
                # Ignora parpadeos extremadamente cortos
                blinking = False
                return

            if blink_duration < long_blink_duration_threshold:  # Parpadeo corto
                click_timestamps.append(current_time)
                if len(click_timestamps) >= 2 and (click_timestamps[-1] - click_timestamps[-2]) < 0.5:
                    pyautogui.doubleClick()  # Doble clic izquierdo
                    print("Doble clic izquierdo")
                    click_timestamps = []  # Reinicia la lista de timestamps
                else:
                    pyautogui.click()  # Clic izquierdo simple
                    print("Clic izquierdo simple")
            elif blink_duration < drag_blink_duration_threshold:  # Parpadeo largo pero no demasiado largo
                pyautogui.click(button='right')  # Clic derecho
                print("Clic derecho")
            elif blink_duration >= drag_blink_duration_threshold and not dragging:  # Parpadeo muy largo para arrastrar
                dragging = True
                pyautogui.mouseDown()
                print("Inicio de arrastre")
            blinking = False

            if dragging and blink_duration < long_blink_duration_threshold:  # Fin del arrastre
                pyautogui.mouseUp()  # Terminar el arrastre
                dragging = False
                print("Fin del arrastre")

try:
    frames = 0
    while True:
        # Captura y procesamiento del frame
        _, frame = cam.read()
        if not _:
            break
        frame = cv2.flip(frame, 1)
        rgb_frame = cv2.cvtColor(frame, cv2.COLOR_BGR2RGB)
        output = face_mesh.process(rgb_frame)
        frame_h, frame_w, _ = frame.shape
        
        if output.multi_face_landmarks:
            landmarks = output.multi_face_landmarks[0].landmark
            nose = landmarks[1]  # Usamos la nariz para la dirección del movimiento
            
            # Coordenadas de la nariz en el frame
            nose_x = int(nose.x * frame_w)
            nose_y = int(nose.y * frame_h)
            cv2.circle(frame, (nose_x, nose_y), 3, (0, 255, 0), -1)

            # Calibración inicial
            if not calibrated:
                frames += 1
                if frames == calibration_frames:
                    calibrated = True
                    recalibrate(nose_x, nose_y, frame_w)
            else:
                # Verifica si la nariz está demasiado lejos del centro de calibración
                if np.linalg.norm(np.array([nose_x, nose_y]) - np.array(calibration_center)) > recalibration_threshold:
                    recalibrate(nose_x, nose_y, frame_w)

                # Dibuja los puntos fijos en el frame
                for point in fixed_points:
                    cv2.circle(frame, point, 3, (255, 0, 0), -1)

                # Encuentra el punto más cercano a la nariz
                closest_point, min_distance = get_closest_point((nose_x, nose_y), fixed_points)
                
                if min_distance < 50:  # Umbral de cercanía para mover el cursor
                    direction_x = (closest_point[0] - nose_x)
                    direction_y = (closest_point[1] - nose_y)
                    direction = (direction_x, direction_y)
                    
                    # Normaliza la dirección para aplicar la velocidad uniformemente
                    norm = np.linalg.norm(direction)
                    if norm != 0:
                        direction = (direction[0] / norm, direction[1] / norm)
                    
                    # Mueve el cursor basado en la dirección normalizada y la velocidad
                    current_x, current_y = pyautogui.position()
                    new_x = current_x + speed * direction[0]
                    new_y = current_y + speed * direction[1]
                    
                    # Asegúrate de que el cursor no se salga de los límites de la pantalla
                    new_x = np.clip(new_x, 0, screen_w)
                    new_y = np.clip(new_y, 0, screen_h)
                    
                    pyautogui.moveTo(new_x, new_y)

            # Visualiza los puntos de los ojos para depuración
            eye_points = [159, 145, 130, 243, 386, 374, 362, 398]
            for point_id in eye_points:
                landmark = landmarks[point_id]
                x = int(landmark.x * frame_w)
                y = int(landmark.y * frame_h)
                cv2.circle(frame, (x, y), 3, (0, 255, 255), -1)

            # Calcula la relación de aspecto del ojo para detectar parpadeos
            ear = calculate_eye_aspect_ratio(landmarks, frame_w, frame_h)
            handle_blinks(ear)

        # Muestra el frame con los puntos fijos
        cv2.imshow('Eye Controlled Mouse', frame)

        # Escucha para la recalibración manual
        key = cv2.waitKey(1)
        if key & 0xFF == ord('r'):  # Presiona 'r' para recalibrar manualmente
            recalibrate(nose_x, nose_y, frame_w)
        elif key & 0xFF == 27:  # Presiona 'ESC' para salir
            break

finally:
    cam.release()
    cv2.destroyAllWindows()
