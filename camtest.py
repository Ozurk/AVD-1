import os
import cv2
# Tell Python to use the physical monitor plugged into the Pi
os.environ["DISPLAY"] = ":0"

# Open the default camera (V4L2 index 0)py 
cap = cv2.VideoCapture(0)

if not cap.isOpened():
    print("Error: Could not open the camera. Check connections.")
    exit()

print("Camera opened successfully. Press 'q' on your keyboard to exit.")

while True:
    ret, frame = cap.read()
    
    if not ret:
        print("Error: Could not read frame.")
        break

    # Show the video feed in a basic window
    cv2.imshow('Camera Test', frame)

    # Press 'q' to quit
    if cv2.waitKey(1) & 0xFF == ord('q'):
        break

# Safely close everything
cap.release()
cv2.destroyAllWindows()