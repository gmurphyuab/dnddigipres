import tkinter as tk
from tkinter import scrolledtext, messagebox
import subprocess
import threading
import os
import re

# Hardcoded output directory — update as needed
HARDCODED_OUTPUT_DIR = "/home/yourusername/VHS_Captures"

# Regex pattern for filename validation: 4 uppercase letters + '_' + 3 uppercase letters + 6 digits
FILENAME_PATTERN = r'^[A-Z]{4}_[A-Z]{3}\d{6}$'

ffmpeg_process = None  # Global to hold subprocess reference

def validate_filename(name):
    return re.match(FILENAME_PATTERN, name) is not None

def start_capture():
    global ffmpeg_process
    if ffmpeg_process is not None:
        messagebox.showwarning("Warning", "Capture is already running.")
        return

    base_name = entry.get().strip()
    if not base_name:
        messagebox.showerror("Error", "Please enter a filename.")
        return

    if not validate_filename(base_name):
        messagebox.showerror("Error", f"Filename must follow the UUID naming convention: Example: DNDP_TES000001")
        return

    os.makedirs(HARDCODED_OUTPUT_DIR, exist_ok=True)

    output_path = os.path.join(HARDCODED_OUTPUT_DIR, f"{base_name}_raw.mkv")

    if os.path.exists(output_path):
        proceed = messagebox.askyesno(
            "File Exists",
            f"The file:\n\n{output_path}\n\nalready exists.\nDo you wish to proceed and overwrite it?"
        )
        if not proceed:
            text_output.insert(tk.END, "Capture canceled by user.\n")
            text_output.see(tk.END)
            return

    text_output.insert(tk.END, f"Starting capture to:\n{output_path}\n\n")
    text_output.see(tk.END)

    # Build FFmpeg + ffplay command with your devices
    command = [
        "ffmpeg",
        "-f", "v4l2",
        "-i", "/dev/video0",
        "-f", "alsa",
        "-i", "hw:2,0",
        "-map", "0:v:0",
        "-map", "1:a:0",
        "-c:v", "ffv1",
        "-level", "3",
        "-coder", "1",
        "-context", "1",
        "-g", "1",
        "-slices", "24",
        "-slicecrc", "1",
        "-c:a", "pcm_s16le",
        "-f", "tee",
        f"[f=mkv]{output_path}|[f=nut]pipe:"
    ]

    # Use Popen with shell=False and pipe stdout, then pipe to ffplay
    # We'll start ffplay separately reading from the pipe

    # To simplify, we will run the full shell command to pipe to ffplay:
    full_command = (
        f'ffmpeg -f v4l2 -i /dev/video0 '
        f'-f alsa -i hw:2,0 '
        f'-map 0:v:0 -map 1:a:0 '
        f'-c:v ffv1 -level 3 -coder 1 -context 1 -g 1 -slices 24 -slicecrc 1 '
        f'-c:a pcm_s16le '
        f'-f tee "[f=mkv]{output_path}|[f=nut]pipe:" | ffplay -'
    )

    def run_ffmpeg():
        global ffmpeg_process
        # Run as shell command because of pipe
        ffmpeg_process = subprocess.Popen(full_command, shell=True,
                                          stdout=subprocess.PIPE,
                                          stderr=subprocess.STDOUT,
                                          text=True,
                                          bufsize=1)

        for line in ffmpeg_process.stdout:
            text_output.insert(tk.END, line)
            text_output.see(tk.END)

        ffmpeg_process.stdout.close()
        ffmpeg_process.wait()
        text_output.insert(tk.END, "\nCapture finished.\n")
        text_output.see(tk.END)
        ffmpeg_process = None  # Reset after finishing

    threading.Thread(target=run_ffmpeg, daemon=True).start()

def stop_capture():
    global ffmpeg_process
    if ffmpeg_process is None:
        messagebox.showinfo("Info", "No capture is currently running.")
        return

    # Send 'q' to ffmpeg process to stop gracefully (equivalent to pressing 'q' in terminal)
    # We can do this by sending SIGINT or writing 'q' to its stdin if supported
    # Since we used shell=True, stdin is None; so let's send SIGINT

    ffmpeg_process.terminate()  # Send SIGTERM, usually ffmpeg stops and finalizes file

    text_output.insert(tk.END, "\nStopping capture...\n")
    text_output.see(tk.END)

root = tk.Tk()
root.title("FFV1 Video Capture to MKV")

tk.Label(root, text="Enter UUID:").pack(pady=(10, 2))
entry = tk.Entry(root, width=40)
entry.pack(pady=2)

frame = tk.Frame(root)
frame.pack(pady=10)

start_button = tk.Button(frame, text="Start Capture", command=start_capture)
start_button.pack(side=tk.LEFT, padx=5)

stop_button = tk.Button(frame, text="Stop Capture", command=stop_capture)
stop_button.pack(side=tk.LEFT, padx=5)

text_output = scrolledtext.ScrolledText(root, height=20, width=100)
text_output.pack(padx=10, pady=(5, 10))

root.mainloop()
