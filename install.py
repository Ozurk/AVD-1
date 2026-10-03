import os
import subprocess
from textwrap import dedent

# -------------------------------
# CONFIGURATION
# -------------------------------
PROJECT_NAME = "AVD-1"
PROJECT_DIR = "/home/admin/AVD-1"
PYTHON_PATH = "/usr/bin/python3" 
ENTRY_FILE = "main.py"  # your main program entry point
SERVICE_FILE = f"/etc/systemd/system/{PROJECT_NAME}.service"
DEPENDENCIES = ["opencv-python", "numpy", "picamera2"]

# -------------------------------
# 1. Install Python dependencies
# -------------------------------
print("Installing dependencies...")
try:
    subprocess.run(
        [PYTHON_PATH, "-m", "pip ", "install ", "--upgrade", "pip"] + DEPENDENCIES,
        check=True,
    )
    print("Dependencies installed successfully.")
except subprocess.CalledProcessError as e:
    print(f" Error installing dependencies: {e}")

# -------------------------------
# 2. Create systemd service file
# -------------------------------
print("⚙️  Creating systemd service...")

service_content = dedent(f"""
    [Unit]
    Description=Counter Defense Project Service
    After=network.target

    [Service]
    Type=simple
    User=admin
    WorkingDirectory={PROJECT_DIR}
    ExecStart={PYTHON_PATH} {PROJECT_DIR}/{ENTRY_FILE}
    Restart=always
    RestartSec=5

    [Install]
    WantedBy=multi-user.target
""")

# Write service file
try:
    with open("/tmp/temp_service.service", "w") as f:
        f.write(service_content)

    # Move it to /etc/systemd/system with sudo
    subprocess.run(["sudo", "mv", "/tmp/temp_service.service", SERVICE_FILE], check=True)
    print(f" Service file created at {SERVICE_FILE}")
except Exception as e:
    print(f" Failed to create service file: {e}")

# -------------------------------
# 3. Enable and start the service
# -------------------------------
print(" Enabling and starting service...")
try:
    subprocess.run(["sudo", "systemctl", "daemon-reload"], check=True)
    subprocess.run(["sudo", "systemctl", "enable", PROJECT_NAME], check=True)
    subprocess.run(["sudo", "systemctl", "start", PROJECT_NAME], check=True)
    print(f" {PROJECT_NAME} service enabled and started successfully.")
except subprocess.CalledProcessError as e:
    print(f" Failed to enable/start service: {e}")

print(" Setup complete!")
