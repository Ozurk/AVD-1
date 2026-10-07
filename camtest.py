import cv2
from picamera2 import Picamera2

# Initialize Picamera2
picam2 = Picamera2()
picam2.configure(picam2.create_preview_configuration(main={"size": (640, 480)}))
picam2.start()

print("Camera opened successfully. Press 'q' to exit.")

while True:
    # Capture frame as a NumPy array (OpenCV format)
    frame = picam2.capture_array()

    # OpenCV uses BGR, Picamera2 outputs RGB by default
    frame = cv2.cvtColor(frame, cv2.COLOR_RGB2BGR)

    cv2.imshow("Camera Test", frame)

    if cv2.waitKey(1) & 0xFF == ord('q'):
        break

cv2.destroyAllWindows()
picam2.stop()