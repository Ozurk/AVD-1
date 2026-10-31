from ultralytics import YOLO

# 1. Load the best checkpoint from train7
model = YOLO(
    r"runs/detect/runs/detect/squirrel_coco-3/weights/best.pt")

# 2. Export to NCNN format (imgsz=416 gives ~30+ FPS on a Pi 5 CPU)
model.export(format="ncnn", imgsz=416)