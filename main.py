import cv2
import customtkinter as ctk
from PIL import Image

import os
# Tell Python to use the primary physical monitor
os.environ["DISPLAY"] = ":0"


# ... rest of your code ...
# Set modern theme
ctk.set_appearance_mode("Dark")
ctk.set_default_color_theme("blue")

class RobotUI(ctk.CTk):
    def __init__(self):
        super().__init__()

        self.title("YOLO Animal Detection")
        
        # 1. Set full screen
        self.attributes('-fullscreen', True)
        
        # Bind the Escape key so you have a way to close the full-screen app
        self.bind("<Escape>", self.quit_app)

        # 2. Initialize Camera 
        # (0 is usually the default Pi Camera if v4l2 is enabled. Change to 1 or higher if needed)
        self.cap = cv2.VideoCapture(0)
        
        # Label to hold the video feed
        self.video_label = ctk.CTkLabel(self, text="")
        self.video_label.pack(fill="both", expand=True)

        # 3. Setup Button in the Top Right
        # Using .place() allows us to float the button over the video feed
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

        # Start the video loop
        self.update_video_feed()

    def update_video_feed(self):
        ret, frame = self.cap.read()
        if ret:
            # Get screen dimensions
            screen_width = self.winfo_screenwidth()
            screen_height = self.winfo_screenheight()

            # Resize the OpenCV frame to fill the screen
            # (cv2.resize is used here because it is much faster than PIL for the Raspberry Pi)
            frame = cv2.resize(frame, (screen_width, screen_height))

            # Convert BGR (OpenCV format) to RGB (PIL format)
            frame = cv2.cvtColor(frame, cv2.COLOR_BGR2RGB)
            image = Image.fromarray(frame)

            # Convert to CTkImage and update the label
            ctk_image = ctk.CTkImage(light_image=image, dark_image=image, size=(screen_width, screen_height))
            self.video_label.configure(image=ctk_image)

        # Schedule the next frame update in ~30ms (approx 30 FPS)
        self.after(30, self.update_video_feed)

    def open_setup_window(self):
        # Check if window is already open to prevent multiple windows
        if self.setup_window is None or not self.setup_window.winfo_exists():
            self.setup_window = ctk.CTkToplevel(self)
            self.setup_window.title("Setup")
            self.setup_window.geometry("350x200")
            
            # Keep the setup window on top of the fullscreen main app
            self.setup_window.attributes('-topmost', True) 
            
            # Center the window on the screen
            self.setup_window.eval('tk::PlaceWindow . center')

            # 4. Setup Window Buttons
            btn_sensitivity = ctk.CTkButton(
                self.setup_window, 
                text="Sensitivity",
                font=("Arial", 14),
                height=40
            )
            btn_sensitivity.pack(pady=(35, 15), padx=40, fill="x")

            btn_target = ctk.CTkButton(
                self.setup_window, 
                text="Target Selection",
                font=("Arial", 14),
                height=40
            )
            btn_target.pack(pady=10, padx=40, fill="x")
        else:
            # If it already exists, just bring it to the front
            self.setup_window.focus()

    def quit_app(self, event=None):
        """Safely release the camera and close the app."""
        if self.cap.isOpened():
            self.cap.release()
        self.destroy()

if __name__ == "__main__":
    app = RobotUI()
    app.mainloop()