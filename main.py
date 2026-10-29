import os
import csv
import cv2
import time
from pathlib import Path
from PIL import Image

import customtkinter as ctk
from picamera2 import Picamera2

# Enforce hardware-timed backend for Raspberry Pi 5
os.environ["GPIOZERO_PIN_FACTORY"] = "lgpio"
import gpiozero

import object_detection
import hw_servo

os.environ["DISPLAY"] = ":0"
CONFIG_PATH = Path(__file__).with_name("config.csv")
TARGETS_PATH = Path(__file__).with_name("targets.csv")

ctk.set_appearance_mode("Dark")
ctk.set_default_color_theme("blue")

class RobotUI(ctk.CTk):
    def __init__(self):
        super().__init__()
        self.title("YOLO Animal Detection")
        
        # 1. Initialize hardware
        self.object_detector = object_detection.ObjectDetector()
        self.pan_servo = hw_servo.Servo(pin=18)
        self.tilt_servo = hw_servo.Servo(pin=19, min_duty=5.0, max_duty=7.0)  
        self.trigger_pin = gpiozero.OutputDevice(17)
        
        # 2. Setup UI
        self.attributes('-fullscreen', True)
        self.bind("<Escape>", self.quit_app)

        # 3. Setup Camera
        self.picam2 = Picamera2()
        self.picam2.configure(self.picam2.create_preview_configuration(main={"size": (640, 480)}))
        self.screen_width = self.winfo_screenwidth()
        self.screen_height = self.winfo_screenheight()
        self.picam2.start()
        
        self.last_detection_time = 0
        self.cached_frame = None 
        self.trigger = {"Engaged": False, "start_time": 0}

        self.video_label = ctk.CTkLabel(self, text="")
        self.video_label.pack(fill="both", expand=True)

        self.setup_btn = ctk.CTkButton(
            self, 
            text="Setup", 
            command=self.open_setup_window, 
            width=120,
            height=40,
            font=("Arial", 16, "bold")
        )
        self.setup_btn.place(relx=1.0, rely=0.0, anchor="ne", x=-20, y=20)

        # Window tracking and Targets
        self.setup_window = None
        self.config_window = None
        self.target_window = None
        self.target_options = ["person", "cat", "dog", "car", "bird"]
        self.target_vars = {target: ctk.BooleanVar(value=True) for target in self.target_options}

        self.class_id_map = {
            "person": 0, "car": 2, "bird": 14, "cat": 15, "dog": 16
        }
        self.object_detector.targets = [self.class_id_map[t] for t in self.target_options]

        self.update_video_feed()

    def engage_trigger(self):
        self.trigger["Engaged"] = True
        self.trigger["start_time"] = time.time()
        self.trigger_pin.on()

    def disengage_trigger(self):
        self.trigger["Engaged"] = False
        self.trigger_pin.off()
        
    def update_video_feed(self):
        frame = self.picam2.capture_array()
        if frame is not None:
            frame = cv2.resize(frame, (320, 240))
            current_time = time.time()
            
            # YOLO Inference Check
            if current_time - self.last_detection_time >= 0:
                self.last_detection_time = current_time
                self.cached_frame, best_center, confidence = self.object_detector.process_frame(frame)
                
                if best_center is not None and confidence > 0.72:
                    target_x, target_y = best_center
                    error_x = target_x - 160
                    error_y = target_y - 120
                    
                    # Proportional Tracking (Adjust decimal for sensitivity)
                    self.pan_servo.move(-1 * error_x * 0.5) 
                    self.tilt_servo.move(-1 * error_y * 0.5)

                    if abs(error_x) < 15 and abs(error_y) < 15:
                        # Target is centered: kill PWM signals to freeze servos without jitter
                        self.pan_servo.relax()
                        self.tilt_servo.relax()
                        
                        if not self.trigger["Engaged"]:
                            # Nod animation
                            for _ in range(15):
                                self.tilt_servo.move(-1)
                                time.sleep(0.02)
                            for _ in range(15):
                                self.tilt_servo.move(1)
                                time.sleep(0.02)
                                
                            self.engage_trigger()

            # Disengage trigger after 2 seconds
            if self.trigger["Engaged"] and (current_time - self.trigger["start_time"] >= 2.0):
                self.disengage_trigger()

            # Render frame
            display_frame = self.cached_frame if self.cached_frame is not None else frame
            image = Image.fromarray(display_frame)
            ctk_image = ctk.CTkImage(light_image=image, dark_image=image, size=(self.screen_width, self.screen_height))
            self.video_label.configure(image=ctk_image)

        self.after(30, self.update_video_feed)

    def open_setup_window(self):
        if self.setup_window is None or not self.setup_window.winfo_exists():
            self.setup_window = ctk.CTkToplevel(self)
            self.setup_window.title("Setup")
            w, h = 350, 200
            x = (self.winfo_screenwidth() - w) // 2
            y = (self.winfo_screenheight() - h) // 2
            self.setup_window.geometry(f"{w}x{h}+{x}+{y}")
            self.setup_window.attributes('-topmost', True) 
            
            ctk.CTkButton(self.setup_window, text="Config", command=self.open_config_window, font=("Arial", 14), height=40).pack(pady=(35, 15), padx=40, fill="x")
            ctk.CTkButton(self.setup_window, text="Target Selection", command=self.open_target_window, font=("Arial", 14), height=40).pack(pady=10, padx=40, fill="x")
            self.setup_window.lift()
            self.setup_window.focus_force()
        else:
            self.setup_window.lift()
            self.setup_window.focus()

    def open_target_window(self):
        if self.target_window is None or not self.target_window.winfo_exists():
            self.target_window = ctk.CTkToplevel(self)
            self.target_window.title("Target Selection")
            w, h = 300, 450
            x = (self.winfo_screenwidth() - w) // 2
            y = (self.winfo_screenheight() - h) // 2
            self.target_window.geometry(f"{w}x{h}+{x}+{y}")
            self.target_window.attributes('-topmost', True)

            ctk.CTkLabel(self.target_window, text="Select Targets:", font=("Arial", 16, "bold")).pack(pady=(15, 10))

            for target in self.target_options:
                ctk.CTkCheckBox(self.target_window, text=target.capitalize(), variable=self.target_vars[target]).pack(pady=8, padx=60, anchor="w")

            ctk.CTkButton(self.target_window, text="Save", command=self.save_targets, height=32).pack(pady=(15, 6))
            self.target_status_label = ctk.CTkLabel(self.target_window, text="")
            self.target_status_label.pack(pady=(0, 8))

            self.target_window.lift()
            self.target_window.focus_force()
        else:
            self.target_window.lift()
            self.target_window.focus()

    def save_targets(self):
        selected_class_ids = []
        with TARGETS_PATH.open("w", newline="", encoding="utf-8") as config_file:
            writer = csv.writer(config_file)
            writer.writerow(["target", "selected"])
            
            for target, var in self.target_vars.items():
                is_selected = var.get()
                writer.writerow([target, str(is_selected)])
                if is_selected:
                    selected_class_ids.append(self.class_id_map[target])

        self.object_detector.targets = selected_class_ids
        self.target_status_label.configure(text="Targets saved to targets.csv!")

    def open_config_window(self):
        if self.config_window is None or not self.config_window.winfo_exists():
            self.config_window = ctk.CTkToplevel(self)
            self.config_window.title("Config")
            w, h = 360, 220
            x = (self.winfo_screenwidth() - w) // 2
            y = (self.winfo_screenheight() - h) // 2
            self.config_window.geometry(f"{w}x{h}+{x}+{y}")
            self.config_window.attributes('-topmost', True)

            self.sensitivity_value_label = ctk.CTkLabel(self.config_window, text="Sensitivity: 50")
            self.sensitivity_value_label.pack(pady=(24, 8))
            
            self.sensitivity_slider = ctk.CTkSlider(self.config_window, from_=0, to=100, number_of_steps=100, command=self.update_sensitivity_value)
            self.sensitivity_slider.set(50)
            self.sensitivity_slider.pack(fill="x", padx=30, pady=(0, 12))

            ctk.CTkButton(self.config_window, text="Save", command=self.save_sensitivity, height=32).pack(pady=(0, 6))
            
            self.config_status_label = ctk.CTkLabel(self.config_window, text="")
            self.config_status_label.pack(pady=(0, 8))

            self.config_window.lift()
            self.config_window.focus_force()
        else:
            self.config_window.lift()
            self.config_window.focus()

    def update_sensitivity_value(self, value):
        self.sensitivity_value_label.configure(text=f"Sensitivity: {int(float(value))}")

    def save_sensitivity(self):
        sensitivity = int(round(self.sensitivity_slider.get()))
        try:
            with CONFIG_PATH.open("r", newline="", encoding="utf-8") as config_file:
                rows = list(csv.reader(config_file))
        except FileNotFoundError:
            rows = []

        sensitivity_row = None
        for row in rows:
            if row and row[0].strip().lower() == "sensitivity":
                sensitivity_row = row
                break

        if sensitivity_row is None:
            rows.append(["sensitivity", str(sensitivity)])
        else:
            if len(sensitivity_row) > 1:
                sensitivity_row[1] = str(sensitivity)
            else:
                sensitivity_row.append(str(sensitivity))

        with CONFIG_PATH.open("w", newline="", encoding="utf-8") as config_file:
            csv.writer(config_file).writerows(rows)

        self.config_status_label.configure(text=f"Saved sensitivity: {sensitivity}")

    def quit_app(self, event=None):
        try:
            self.picam2.stop()
        except Exception:
            pass
        self.destroy()

if __name__ == "__main__":
    app = RobotUI()
    app.mainloop()