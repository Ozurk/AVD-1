import csv
import cv2
import customtkinter as ctk
from PIL import Image, ImageTk
from pathlib import Path
import os
from picamera2 import Picamera2
import object_detection
import time

# Tell Python to use the primary physical monitor
os.environ["DISPLAY"] = ":0"
CONFIG_PATH = Path(__file__).with_name("config.csv")

# Set modern theme
ctk.set_appearance_mode("Dark")
ctk.set_default_color_theme("blue")

class RobotUI(ctk.CTk):
    def __init__(self):
        super().__init__()

        self.title("YOLO Animal Detection")
        self.object_detector = object_detection.ObjectDetector()
        # 1. Set full screen
        self.attributes('-fullscreen', True)
        # Bind the Escape key so you have a way to close the full-screen app
        self.bind("<Escape>", self.quit_app)

        # 2. Initialize Picamera2
        self.picam2 = Picamera2()
        self.picam2.configure(self.picam2.create_preview_configuration(main={"size": (640, 480)}))
        self.screen_width = self.winfo_screenwidth()
        self.screen_height = self.winfo_screenheight()
        self.picam2.start()
        self.last_detection_time = 0
        self.cached_frame = None  # Store the last processed frame

        # Label to hold the video feed
        self.video_label = ctk.CTkLabel(self, text="")
        self.video_label.pack(fill="both", expand=True)

        # 3. Setup Button in the Top Right
        self.setup_btn = ctk.CTkButton(
            self, 
            text="Setup", 
            command=self.open_setup_window, 
            width=120,
            height=40,
            font=("Arial", 16, "bold")
        )
        self.setup_btn.place(relx=1.0, rely=0.0, anchor="ne", x=-20, y=20)

        # Variable to keep track of the setup window
        self.setup_window = None
        self.config_window = None

        # Start the video loop
        self.update_video_feed()

    def update_video_feed(self):
        frame = self.picam2.capture_array()
        if frame is not None:
            frame = cv2.flip(frame, 0)
            
            # Run YOLO every 2 seconds to keep GUI responsive
            current_time = time.time()
            if current_time - self.last_detection_time >= 2.0:
                self.last_detection_time = current_time
                # Process frame array and return annotated frame
                self.cached_frame = self.object_detector.process_frame(frame)
            
            # Display the marked-up frame (or raw frame if waiting)
            display_frame = self.cached_frame if self.cached_frame is not None else frame
            
            # Convert to PIL and update CTkImage
            image = Image.fromarray(display_frame)
            ctk_image = ctk.CTkImage(light_image=image, dark_image=image, size=(self.screen_width, self.screen_height))
            self.video_label.configure(image=ctk_image)

        self.after(30, self.update_video_feed)

    def open_setup_window(self):
        if self.setup_window is None or not self.setup_window.winfo_exists():
            self.setup_window = ctk.CTkToplevel(self)
            self.setup_window.title("Setup")
            window_width = 350
            window_height = 200
            window_x = (self.winfo_screenwidth() - window_width) // 2
            window_y = (self.winfo_screenheight() - window_height) // 2
            self.setup_window.geometry(
                f"{window_width}x{window_height}+{window_x}+{window_y}"
            )
            
            self.setup_window.attributes('-topmost', True) 
            
            btn_config = ctk.CTkButton(
                self.setup_window, 
                text="Config",
                command=self.open_config_window,
                font=("Arial", 14),
                height=40
            )
            btn_config.pack(pady=(35, 15), padx=40, fill="x")

            btn_target = ctk.CTkButton(
                self.setup_window, 
                text="Target Selection",
                font=("Arial", 14),
                height=40
            )
            btn_target.pack(pady=10, padx=40, fill="x")
            self.setup_window.lift()
            self.setup_window.focus_force()
        else:
            self.setup_window.lift()
            self.setup_window.focus()

    def open_config_window(self):
        if self.config_window is None or not self.config_window.winfo_exists():
            self.config_window = ctk.CTkToplevel(self)
            self.config_window.title("Config")
            window_width = 360
            window_height = 220
            window_x = (self.winfo_screenwidth() - window_width) // 2
            window_y = (self.winfo_screenheight() - window_height) // 2
            self.config_window.geometry(
                f"{window_width}x{window_height}+{window_x}+{window_y}"
            )
            self.config_window.attributes('-topmost', True)

            self.sensitivity_value_label = ctk.CTkLabel(
                self.config_window, text="Sensitivity: 50"
            )
            self.sensitivity_value_label.pack(pady=(24, 8))
            self.sensitivity_slider = ctk.CTkSlider(
                self.config_window,
                from_=0,
                to=100,
                number_of_steps=100,
                command=self.update_sensitivity_value,
            )
            self.sensitivity_slider.set(50)
            self.sensitivity_slider.pack(fill="x", padx=30, pady=(0, 12))

            save_button = ctk.CTkButton(
                self.config_window,
                text="Save",
                command=self.save_sensitivity,
                height=32,
            )
            save_button.pack(pady=(0, 6))
            self.config_status_label = ctk.CTkLabel(self.config_window, text="")
            self.config_status_label.pack(pady=(0, 8))

            self.config_window.lift()
            self.config_window.focus_force()
        else:
            self.config_window.lift()
            self.config_window.focus()

    def update_sensitivity_value(self, value):
        self.sensitivity_value_label.configure(
            text=f"Sensitivity: {int(float(value))}"
        )

    def save_sensitivity(self):
        sensitivity = int(round(self.sensitivity_slider.get()))
        with CONFIG_PATH.open("r", newline="", encoding="utf-8") as config_file:
            rows = list(csv.reader(config_file))

        sensitivity_row = None
        for row in rows:
            if row and row[0].strip().lower() == "sensitivity":
                sensitivity_row = row
                break

        if sensitivity_row is None:
            self.config_status_label.configure(
                text="Sensitivity key not found in config.csv"
            )
            return

        if len(sensitivity_row) > 1:
            sensitivity_row[1] = str(sensitivity)
        else:
            sensitivity_row.append(str(sensitivity))

        with CONFIG_PATH.open("w", newline="", encoding="utf-8") as config_file:
            csv.writer(config_file).writerows(rows)

        self.config_status_label.configure(text=f"Saved sensitivity: {sensitivity}")

    def quit_app(self, event=None):
        """Safely release the camera and close the app."""
        try:
            self.picam2.stop()
        except Exception:
            pass
        self.destroy()

if __name__ == "__main__":
    app = RobotUI()
    app.mainloop()