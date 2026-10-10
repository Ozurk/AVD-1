import cv2
from ultralytics import YOLO

class ObjectDetector():
    def __init__(self, model_path="yolov8n_ncnn_model", targets: list = None):
        if targets is None:
            targets = []
            
        # Load the YOLO model once during initialization
        self.model = YOLO(model_path)
        print(f"Loaded YOLO model from {model_path}")
        self.targets = targets  # List of target class IDs to detect
        self.primary_target = None
        
    def process_frame(self, frame):
        """
        Accepts an image frame (NumPy array), runs YOLO object detection,
        draws bounding boxes and labels on the frame, and returns it
        along with the (x, y) center coordinate of the highest confidence detection.
        """
        if frame is None:
            return frame, None

        # Skip inference completely if no targets are selected
        if not self.targets:
            return frame, None

        # Run inference on the input frame, filtering by selected class IDs
        results = self.model(frame, classes=self.targets, verbose=False)

        best_confidence = -1.0
        best_center = None

        # Draw bounding boxes and labels
        for result in results:
            for box in result.boxes:
                x1, y1, x2, y2 = map(int, box.xyxy[0])
                confidence = float(box.conf[0])
                class_id = int(box.cls[0])
                label = f"{self.model.names[class_id]} {confidence:.2f}"

                # Calculate center coordinates
                center_x = (x1 + x2) // 2
                center_y = (y1 + y2) // 2

                # Check if this is the highest confidence detection so far
                if confidence > best_confidence:
                    best_confidence = confidence
                    best_center = (center_x, center_y)

                # Draw bounding box (Green)
                cv2.rectangle(frame, (x1, y1), (x2, y2), (0, 255, 0), 2)
                cv2.circle(frame, (center_x, center_y), 5, (255, 0, 0), -1)  # Center

                # Get label text dimensions
                (text_width, text_height), baseline = cv2.getTextSize(
                    label, cv2.FONT_HERSHEY_SIMPLEX, 0.5, 1
                )
                
                # Draw filled background rectangle for text readability
                cv2.rectangle(
                    frame,
                    (x1, y1 - text_height - 5),
                    (x1 + text_width, y1),
                    (0, 255, 0),
                    -1,
                )
                print(f"Detected {label} at [{x1}, {y1}, {x2}, {y2}] with confidence {confidence:.2f}")

                # Draw text over background
                cv2.putText(
                    frame,
                    label,
                    (x1, y1 - 5),
                    cv2.FONT_HERSHEY_SIMPLEX,
                    0.5,
                    (255, 255, 255),
                    1,
                    cv2.LINE_AA,
                )

        return frame, best_center