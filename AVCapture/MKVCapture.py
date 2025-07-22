import tkinter as tk
from tkinter import messagebox
import re
import subprocess
import os
import signal

# === HARD-CODED SAVE DIRECTORY ===
SAVE_DIR = "/home/yourusername/captures"  # Change this to your actual path

# === AUDIO AND VIDEO DEVICES ===
AUDIO_DEVICE = "hw:2,0"
VIDEO_DEVICE = "/dev/video0"

ffmpeg_process = None

def validate_filename(name):
    pattern = r"^[A-Z]{4}_[A-Z]{3}\d{6}$"
    return re.match(pattern, name)

def start_capture():
    global ffmpeg_process

    base_name = filename_entry.get().strip()

    if not validate_filename(base_name):
        messagebox.showerror("Invalid Filename", "Filename must match: AAAA_BBB000000")
        return

    output_path = os.path.join(SAVE_DIR, f"{base_name}_raw.mkv")

    if os.path.exists(output_path):
        overwrite = messagebox.askyesno("File Exists", "This file name already exists. Do you wish to proceed and overwrite the existing file?")
        if not overwrite:
            return
        os.remove(output_path)

    # FFmpeg command
    cmd = [
        "ffmpeg",
        "-f", "v4l2", "-i", VIDEO_DEVICE,
        "-f", "alsa", "-i", AUDIO_DEVICE,
        "-c:v", "ffv1", "-level", "3", "-coder", "1", "-context", "1", "-g", "1",
        "-slices", "24", "-slicecrc", "1",
        "-c:a", "pcm_s16le",
        "-map", "0:v", "-map", "1:a",
        "-f", "tee",
        f"[f=mkv]{output_path}|[f=mpegts]udp://127.0.0.1:1234?pkt_size=1316"
    ]

    try:
        ffmpeg_process = subprocess.Popen(
            cmd,
            stdout=subprocess.PIPE,
            stderr=subprocess.STDOUT,
            text=True
        )
        log_output.insert(tk.END, f"Started capturing to:\n{output_path}\n\n")
        log_output.see(tk.END)
        root.after(100, read_ffmpeg_output)
    except Exception as e:
        messagebox.showerror("Error", f"Failed to start ffmpeg:\n{e}")

def read_ffmpeg_output():
    if ffmpeg_process and ffmpeg_process.poll() is None:
        line = ffmpeg_process.stdout.readline()
        if line:
            log_output.insert(tk.END, line)
            log_output.see(tk.END)
        root.after(100, read_ffmpeg_output)

def stop_capture():
    global ffmpeg_process
    if ffmpeg_process and ffmpeg_process.poll() is None:
        log_output.insert(tk.END, "\nStopping capture...\n")
        ffmpeg_process.send_signal(signal.SIGINT)
        ffmpeg_process.wait()
        log_output.insert(tk.END, "Capture stopped. File finalized.\n")
        log_output.see(tk.END)
    else:
        messagebox.showinfo("Not Running", "FFmpeg is not currently capturing.")

# === GUI ===
root = tk.Tk()
root.title("VHS Capture GUI")

frame = tk.Frame(root, padx=10, pady=10)
frame.pack()

tk.Label(frame, text="Enter filename (AAAA_BBB000000):").grid(row=0, column=0, sticky="w")
filename_entry = tk.Entry(frame, width=30)
filename_entry.grid(row=0, column=1)

start_button = tk.Button(frame, text="Start Capture", command=start_capture, bg="green", fg="white")
start_button.grid(row=1, column=0, pady=10)

stop_button = tk.Button(frame, text="Stop Capture", command=stop_capture, bg="red", fg="white")
stop_button.grid(row=1, column=1, pady=10)

log_output = tk.Text(root, height=20, width=80)
log_output.pack(padx=10, pady=(0, 10))

root.mainloop()
