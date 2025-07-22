import tkinter as tk
from tkinter import messagebox, scrolledtext
import subprocess
import os
import re
import signal

# === CONFIGURATION ===
OUTPUT_DIR = "/home/yourusername/captures"  # <-- Change this to your actual save path
VIDEO_DEVICE = "/dev/video0"
AUDIO_DEVICE = "hw:2,0"
FFMPEG_PATH = "ffmpeg"

FILENAME_PATTERN = re.compile(r'^[A-Z]{4}_[A-Z]{3}\d{6}$')
ffmpeg_process = None

# === FUNCTIONS ===
def start_capture():
    global ffmpeg_process

    filename = filename_entry.get().strip()
    if not FILENAME_PATTERN.match(filename):
        messagebox.showerror("Invalid Filename", "Use UUID format.")
        return

    output_file = os.path.join(OUTPUT_DIR, filename + "_raw.mkv")

    if os.path.exists(output_file):
        if not messagebox.askyesno("Overwrite?", f"{output_file} already exists.\nDo you want to overwrite it?"):
            return

    command = [
        FFMPEG_PATH,
        "-f", "v4l2", "-i", VIDEO_DEVICE,
        "-f", "alsa", "-i", AUDIO_DEVICE,
        "-c:v", "ffv1", "-level", "3", "-coder", "1", "-context", "1", "-g", "1",
        "-slices", "24", "-slicecrc", "1",
        "-c:a", "pcm_s16le",
        "-map", "0:v", "-map", "1:a",
        output_file
    ]

    try:
        ffmpeg_process = subprocess.Popen(
            command,
            stdout=subprocess.PIPE,
            stderr=subprocess.STDOUT,
            text=True,
            bufsize=1
        )
        output_text.insert(tk.END, f"Started capture to: {output_file}\n")
        start_button.config(state=tk.DISABLED)
        stop_button.config(state=tk.NORMAL)
        window.after(100, read_ffmpeg_output)
    except Exception as e:
        messagebox.showerror("FFmpeg Error", str(e))
        ffmpeg_process = None

def read_ffmpeg_output():
    if ffmpeg_process and ffmpeg_process.stdout:
        line = ffmpeg_process.stdout.readline()
        if line:
            output_text.insert(tk.END, line)
            output_text.see(tk.END)
        if ffmpeg_process.poll() is None:
            window.after(100, read_ffmpeg_output)
        else:
            output_text.insert(tk.END, "\nCapture completed.\n")
            start_button.config(state=tk.NORMAL)
            stop_button.config(state=tk.DISABLED)
    else:
        output_text.insert(tk.END, "No FFmpeg process running.\n")

def stop_capture():
    global ffmpeg_process
    if ffmpeg_process and ffmpeg_process.poll() is None:
        ffmpeg_process.send_signal(signal.SIGINT)
        output_text.insert(tk.END, "Stopping capture (this may take a few seconds)...\n")
    else:
        messagebox.showinfo("Info", "Capture is not currently running.")

# === GUI SETUP ===
window = tk.Tk()
window.title("Video Tape Capture")
window.geometry("700x500")

tk.Label(window, text="Enter UUID: ").pack(pady=5)
filename_entry = tk.Entry(window, width=40)
filename_entry.pack()

btn_frame = tk.Frame(window)
btn_frame.pack(pady=10)
start_button = tk.Button(btn_frame, text="Start Capture", command=start_capture, width=20)
start_button.pack(side=tk.LEFT, padx=10)
stop_button = tk.Button(btn_frame, text="Stop Capture", command=stop_capture, width=20, state=tk.DISABLED)
stop_button.pack(side=tk.RIGHT, padx=10)

output_text = scrolledtext.ScrolledText(window, height=20, width=80)
output_text.pack(pady=10)

window.mainloop()
