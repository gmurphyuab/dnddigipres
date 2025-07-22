import tkinter as tk
from tkinter import messagebox, scrolledtext
import subprocess
import os
import re
import signal
import threading

# === CONFIGURATION ===
OUTPUT_DIR = "/home/yourusername/captures"  # Change this to your actual path
VIDEO_DEVICE = "/dev/video0"
AUDIO_DEVICE = "hw:2,0"
FILENAME_REGEX = re.compile(r'^[A-Z]{4}_[A-Z]{3}\d{6}$')

ffmpeg_process = None
ffmpeg_thread = None

# === FUNCTIONS ===

def validate_filename(name):
    return bool(FILENAME_REGEX.match(name))

def start_capture():
    global ffmpeg_process, ffmpeg_thread

    base_name = filename_entry.get().strip()
    if not validate_filename(base_name):
        messagebox.showerror("Invalid Filename", "Use format: AAAA_BBB000000")
        return

    full_filename = f"{base_name}_raw.mkv"
    output_path = os.path.join(OUTPUT_DIR, full_filename)

    if os.path.exists(output_path):
        if not messagebox.askyesno("File Exists", f"{output_path} already exists.\nDo you want to overwrite it?"):
            return

    command = [
        "ffmpeg",
        "-f", "v4l2", "-thread_queue_size", "512", "-i", VIDEO_DEVICE,
        "-f", "alsa", "-thread_queue_size", "512", "-i", AUDIO_DEVICE,
        "-c:v", "ffv1", "-level", "3", "-coder", "1", "-context", "1", "-g", "1",
        "-slices", "24", "-slicecrc", "1",
        "-c:a", "pcm_s16le",
        "-map", "0:v", "-map", "1:a",
        "-y",  # always overwrite
        output_path
    ]

    def run_ffmpeg():
        global ffmpeg_process
        try:
            ffmpeg_process = subprocess.Popen(
                command,
                stdout=subprocess.PIPE,
                stderr=subprocess.STDOUT,
                text=True
            )
            for line in ffmpeg_process.stdout:
                output_box.insert(tk.END, line)
                output_box.see(tk.END)
            ffmpeg_process.wait()
            output_box.insert(tk.END, "\nCapture finished.\n")
        except Exception as e:
            output_box.insert(tk.END, f"\nError: {str(e)}\n")
        finally:
            start_button.config(state=tk.NORMAL)
            stop_button.config(state=tk.DISABLED)

    start_button.config(state=tk.DISABLED)
    stop_button.config(state=tk.NORMAL)
    output_box.insert(tk.END, f"Starting capture: {output_path}\n")
    ffmpeg_thread = threading.Thread(target=run_ffmpeg, daemon=True)
    ffmpeg_thread.start()

def stop_capture():
    global ffmpeg_process
    if ffmpeg_process and ffmpeg_process.poll() is None:
        output_box.insert(tk.END, "Stopping capture (this may take a few seconds)...\n")
        ffmpeg_process.send_signal(signal.SIGINT)
        stop_button.config(state=tk.DISABLED)
    else:
        messagebox.showinfo("Not Running", "No capture is currently running.")

# === GUI SETUP ===

window = tk.Tk()
window.title("VHS/Beta Tape Archival Capture")
window.geometry("700x500")

tk.Label(window, text="Enter filename (format: AAAA_BBB000000)").pack(pady=5)
filename_entry = tk.Entry(window, width=40)
filename_entry.pack(pady=5)

button_frame = tk.Frame(window)
button_frame.pack(pady=10)

start_button = tk.Button(button_frame, text="Start Capture", width=20, command=start_capture)
start_button.pack(side=tk.LEFT, padx=10)

stop_button = tk.Button(button_frame, text="Stop Capture", width=20, command=stop_capture, state=tk.DISABLED)
stop_button.pack(side=tk.RIGHT, padx=10)

output_box = scrolledtext.ScrolledText(window, width=85, height=20)
output_box.pack(padx=10, pady=10)

window.mainloop()
