import os
import subprocess
from textwrap import dedent

# -------------------------------
# CONFIGURATION
# -------------------------------
PROJECT_NAME = "AVD-1"
PROJECT_DIR = "/home/admin/AVD-1"
PYTHON_PATH = "/usr/bin/python3" 
ENTRY_FILE = "main.py"
SERVICE_FILE = f"/etc/systemd/system/{PROJECT_NAME}.service"

# -------------------------------
# 1. Install Dependencies Safely
# -------------------------------
print("Installing PyTorch (CPU-only) to save storage...")
try:
    # Install CPU Torch first to prevent gigabytes of useless CUDA/NVIDIA downloads
    subprocess.run(
        [PYTHON_PATH, "-m", "pip", "install", "torch", "torchvision", 
         "--index-url", "https://download.pytorch.org/whl/cpu", 
         "--break-system-packages"],
        check=True
    )
    
    print("Installing remaining project dependencies...")
    # picamera2 is omitted because it is pre-installed via apt on Raspberry Pi OS; 
    # installing it via pip usually causes conflicts.
    DEPENDENCIES = ["ultralytics", "opencv-python", "numpy", "customtkinter", "Pillow", "gpiozero", "NCNN", "rpi_hardware_pwm"]
    subprocess.run(
        ["sudo"PYTHON_PATH, "-m", "pip", "install", "--upgrade"] + DEPENDENCIES + ["--break-system-packages"],
        check=True
    )
    print("Dependencies installed successfully.")
except subprocess.CalledProcessError as e:
    print(f"Error installing dependencies: {e}")
    exit(1)

# -------------------------------
# 2. Create systemd service file
# -------------------------------
print("⚙️  Creating systemd service...")

# Note: GUI apps require specific environment variables to render on the desktop via systemd.
# The user ID is assumed to be 1000 (default for the first user).
service_content = dedent(f"""\
    [Unit]
    Description=Animal Vision Defense (AVD-1)
    After=graphical.target network.target

    [Service]
    Type=simple
    User=admin
    Environment="DISPLAY=:0"
    Environment="WAYLAND_DISPLAY=wayland-1"
    Environment="XDG_RUNTIME_DIR=/run/user/1000"
    WorkingDirectory={PROJECT_DIR}
    ExecStart={PYTHON_PATH} {PROJECT_DIR}/{ENTRY_FILE}
    Restart=always
    RestartSec=5

    [Install]
    WantedBy=graphical.target
""")

# Write service file
try:
    with open("/tmp/temp_service.service", "w") as f:
        f.write(service_content)

    # Move it to /etc/systemd/system with sudo and set permissions
    subprocess.run(["sudo", "mv", "/tmp/temp_service.service", SERVICE_FILE], check=True)
    subprocess.run(["sudo", "chmod", "644", SERVICE_FILE], check=True)
    print(f"Service file created at {SERVICE_FILE}")
except Exception as e:
    print(f"Failed to create service file: {e}")
    exit(1)

# -------------------------------
# 3. Enable and start the service
# -------------------------------
print("Enabling and starting service...")
try:
    subprocess.run(["sudo", "systemctl", "daemon-reload"], check=True)
    subprocess.run(["sudo", "systemctl", "enable", PROJECT_NAME], check=True)
    subprocess.run(["sudo", "systemctl", "restart", PROJECT_NAME], check=True)
    print(f"{PROJECT_NAME} service enabled and started successfully.")
except subprocess.CalledProcessError as e:
    print(f"Failed to enable/start service: {e}")

print("Setup complete!")