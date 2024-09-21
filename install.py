import os
import subprocess
import sys

def install_required_packages():
    required_packages = [
        'customtkinter',
        'requests',
        'pystray',
        'Pillow',
        'pybip39',
        'PyInstaller'
    ]

    for package in required_packages:
        try:
            __import__(package)
        except ImportError:
            print(f"Installing {package}...")
            subprocess.check_call([sys.executable, '-m', 'pip', 'install', package])

def build_executable():
    current_dir = os.path.dirname(os.path.realpath(__file__))
    icon_path = os.path.join(current_dir, "erwin.ico")
    script_path = os.path.join(current_dir, "erwin.py")
    output_dir = os.path.join(os.path.expanduser("~"), "Desktop")

    if not os.path.exists(icon_path):
        print(f"Error: Icon file not found at {icon_path}")
        return

    os.makedirs(output_dir, exist_ok=True)

    command = [
        sys.executable, "-m", "PyInstaller",
        "--add-data", f"{icon_path};.",
        "--noconsole",
        "--name=Erwin",
        f"--icon={icon_path}",
        f"--distpath={output_dir}",
        "--onedir",
        script_path
    ]

    try:
        subprocess.run(command, check=True)
        print(f"Executable created successfully in {output_dir}")
        print("Icon included in the application bundle")
    except subprocess.CalledProcessError as e:
        print(f"Error creating executable: {e}")
    except Exception as e:
        print(f"An unexpected error occurred: {e}")

if __name__ == "__main__":
    install_required_packages()
    build_executable()
