import os
import subprocess
import venv
from textwrap import dedent

# -------------------------------
# CONFIGURATION
# -------------------------------
PROJECT_NAME = "AVD-1"
PROJECT_DIR = "/home/admin/AVD-1"
VENV_DIR = os.path.join(PROJECT_DIR, ".venv")
# Use the virtual environment's Python executable
VENV_PYTHON = os.path.join(VENV_DIR, "bin", "python")
ENTRY_FILE = "main.py"
SERVICE_FILE = f"/etc/systemd/system/{PROJECT_NAME}.service"

# -------------------------------
# 1. Create Virtual Environment
# -------------------------------
print(f"Creating virtual environment at {VENV_DIR}...")
try:
    # --system-site-packages is required to access apt-installed packages like picamera2
    venv.create(VENV_DIR, with_pip=True, system_site_packages=True)
    print("Virtual environment created.")
except Exception as e:
    print(f"Error creating virtual environment: {e}")
    exit(1)

# -------------------------------
# 2. Install Dependencies Safely
# -------------------------------
print("Installing PyTorch (CPU-only) to save storage...")
try:
    # Install using the venv Python, removed --break-system-packages
    subprocess.run(
        [VENV_PYTHON, "-m", "pip", "install", "torch", "torchvision", 
         "--index-url", "https://download.pytorch.org/whl/cpu"],
        check=True
    )
    
    print("Installing remaining project dependencies...")
    DEPENDENCIES = ["ultralytics", "opencv-python", "numpy", "customtkinter", "Pillow", "gpiozero", "NCNN", "rpi_hardware_pwm"]
    
    # Removed 'sudo' and '--break-system-packages' as we are installing into the local venv
    subprocess.run(
        [VENV_PYTHON, "-m", "pip", "install", "--upgrade"] + DEPENDENCIES,
        check=True
    )
    print("Dependencies installed successfully.")
except subprocess.CalledProcessError as e:
    print(f"Error installing dependencies: {e}")
    exit(1)

# -------------------------------
# 3. Create systemd service file
# -------------------------------
print("⚙️  Creating systemd service...")

# Note: GUI apps require specific environment variables to render on the desktop via systemd.
# The ExecStart now points to the virtual environment's Python.
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
    ExecStart={VENV_PYTHON} {PROJECT_DIR}/{ENTRY_FILE}
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
# 4. Enable and start the service
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