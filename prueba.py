import cv2

cap = cv2.VideoCapture(0)

if not cap.isOpened():
    print("No se pudo abrir la cámara.")
else:
    print("Cámara abierta exitosamente.")

while True:
    ret, frame = cap.read()

    if not ret:
        print("Error al capturar la imagen de la cámara.")
        break

    cv2.imshow('Webcam', frame)

    if cv2.waitKey(1) & 0xFF == ord('q'):
        break

cap.release()
cv2.destroyAllWindows()