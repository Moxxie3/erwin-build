import os
import subprocess
import sys

def create_executable():
    desktop_path = os.path.join(os.path.expanduser('~'), 'Desktop')

    erwin_app_path = os.path.join(desktop_path, 'Erwin')
    os.makedirs(erwin_app_path, exist_ok=True)

    pyinstaller_command = [
        sys.executable,
        '-m',
        'PyInstaller',
        '--onefile',
        '--noconsole',
        '--icon=erwin.ico',
        f'--distpath={erwin_app_path}',
        'Erwin.py'
    ]
    try:
        subprocess.run(pyinstaller_command, check=True)
        print(f"Executable created successfully in {erwin_app_path}")
    except subprocess.CalledProcessError as e:
        print(f"Error creating executable: {e}")
    except Exception as e:
        print(f"An unexpected error occurred: {e}")

if __name__ == "__main__":
    create_executable()