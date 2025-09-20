import pystray
from PIL import Image, ImageDraw
import subprocess
import time
import sys
import threading
import signal
import os
from datetime import datetime

# Global variable to store the running process
bot_process = None
icon = None

# --- Configuration ---
# The directory where your bot executable is located.
SCRIPT_DIR = './EXE'

# The command to run the bot executable.
BOT_COMMAND = [os.path.join(SCRIPT_DIR, 'StudioPresence.exe')]

# --- Helper Functions for UI and State Management ---
def create_image(width, height, color1, color2):
    """Generates a simple square image for the tray icon."""
    image = Image.new('RGB', (width, height), color1)
    dc = ImageDraw.Draw(image)
    dc.rectangle(
        (width // 2, 0, width, height // 2),
        fill=color2
    )
    dc.rectangle(
        (0, height // 2, width // 2, height),
        fill=color2
    )
    return image

def set_icon_status(is_running):
    """
    Changes the tray icon to reflect the service status.
    Green for running, red for stopped.
    """
    global icon
    if is_running:
        icon.icon = create_image(64, 64, '#00C853', '#009624')  # Green color
        icon.title = "RP Running"
    else:
        icon.icon = create_image(64, 64, '#F44336', '#D32F2F')  # Red color
        icon.title = "RP Stopped"

# --- Service Control Functions ---
def run_command_in_background(command, process_name):
    """
    Starts a process in the background and returns the process object.
    It uses `creationflags` for Windows to hide the console window and
    pipes all output to a log file.
    """
    # Create the log directory if it doesn't exist
    log_dir = os.path.join(os.path.expanduser("~"), "Documents", "UnforePrograms", "StudioPresence", 'logs')
    os.makedirs(log_dir, exist_ok=True)
    
    # Create a unique filename with the current date and time
    timestamp = datetime.now().strftime('%Y-%m-%d_%H-%M-%S')
    log_file_path = os.path.join(log_dir, f'{timestamp}.log')
    
    print(f"Starting process: {' '.join(command)}")
    print(f"All output will be redirected to: {log_file_path}")

    try:
        # Open the log file for writing
        with open(log_file_path, 'w') as log_file:
            # Start the process and redirect both stdout and stderr to the log file
            executable = command[0]
            proc = subprocess.Popen(
                command,
                cwd=os.path.dirname(executable), 
                creationflags=subprocess.CREATE_NO_WINDOW,
                stdout=log_file,
                stderr=subprocess.STDOUT,
            )
        return proc

    except FileNotFoundError:
        print(f"Error: Command '{command[0]}' not found. "
              "Please check if the path is correct.")
        set_icon_status(False)
        return None
    except Exception as e:
        print(f"An unexpected error occurred: {e}")
        set_icon_status(False)
        return None

def start_services(icon, item):
    """Starts the bot service."""
    global bot_process
    print("Attempting to start bot...")
    
    # Check if the executable file actually exists
    if not os.path.isfile(BOT_COMMAND[0]):
        print(f"Error: Executable not found at {BOT_COMMAND[0]}")
        set_icon_status(False)
        return

    if bot_process and bot_process.poll() is None:
        print("Bot is already running.")
    else:
        bot_process = run_command_in_background(BOT_COMMAND, "StudioPres")

    if bot_process:
        print("Bot started successfully.")
        set_icon_status(True)
    else:
        print("Failed to start bot.")
        set_icon_status(False)

def stop_services(icon, item):
    """Stops the bot service."""
    global bot_process
    print("Attempting to stop bot...")

    if bot_process and bot_process.poll() is None:
        bot_process.terminate()
        time.sleep(1) # Give it a moment to terminate
        if bot_process.poll() is None:
            bot_process.kill()
        print("Bot service stopped.")
        bot_process = None

    set_icon_status(False)
    print("All services stopped.")

def exit_app(icon, item):
    """Stops services and exits the application gracefully."""
    print("Exiting application...")
    stop_services(icon, item)
    icon.stop()

def main():
    """Main function to create and run the tray icon."""
    global icon
    
    # Create the menu for the tray icon
    menu = (
        pystray.MenuItem('UnforePresence', exit_app),
        pystray.Menu.SEPARATOR,
        pystray.MenuItem('Exit', exit_app) # Corrected: Call exit_app to stop the icon
    )

    # Create the icon object
    icon = pystray.Icon(
        'service_manager',
        icon=create_image(64, 64, '#F44336', '#D32F2F'), # Default to red (stopped)
        title='Bot Stopped',
        menu=menu
    )

    # Signal handler for graceful shutdown on Ctrl+C
    def signal_handler(sig, frame):
        print('Signal received, stopping icon...')
        icon.stop()
        sys.exit(0)
    
    signal.signal(signal.SIGINT, signal_handler)

    start_services(icon, "hi")

    # Corrected: Added back icon.run() to keep the application running
    icon.run()

if __name__ == '__main__':
    main()