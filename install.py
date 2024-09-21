import os
import subprocess

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
        "python", "-m", "PyInstaller",
        "--add-data", f"{icon_path};.",
        "--noconsole",
        "--name=Erwin",
        f"--icon={icon_path}",
        f"--distpath={output_dir}",
        "--onedir",
        "--hidden-import=customtkinter",
        "--hidden-import=requests",
        "--hidden-import=json",
        "--hidden-import=random",
        "--hidden-import=time",
        "--hidden-import=threading",
        "--hidden-import=tkinter",
        "--hidden-import=tkinter.filedialog",
        "--hidden-import=tkinter.messagebox",
        "--hidden-import=pystray",
        "--hidden-import=PIL",
        "--hidden-import=PIL.Image",
        "--hidden-import=pybip39",
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
    build_executable()
