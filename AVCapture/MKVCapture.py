import tkinter as tk
from tkinter import scrolledtext, messagebox
import subprocess
import threading
import os

# 🔧 Hardcoded output directory — change this to your desired path
HARDCODED_OUTPUT_DIR = "/home/yourusername/VHS_Captures"

def start_capture():
    base_name = entry.get().strip()
    if not base_name:
        messagebox.showerror("Error", "Please enter a filename.")
        return

    os.makedirs(HARDCODED_OUTPUT_DIR, exist_ok=True)

    output_path = os.path.join(HARDCODED_OUTPUT_DIR, f"{base_name}_raw.mkv")

    # Check if file exists and prompt user
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

    # FFmpeg + ffplay tee command
    command = f"""ffmpeg -f v4l2 -i /dev/video1 \
-f alsa -i hw:1,0 \
-map 0:v:0 -map 1:a:0 \
-c:v ffv1 -level 3 -coder 1 -context 1 -g 1 -slices 24 -slicecrc 1 \
-c:a pcm_s16le \
-f tee "[f=mkv]{output_path}|[f=nut]pipe:" | ffplay -"""

    def run_ffmpeg():
        process = subprocess.Popen(command, shell=True, stdout=subprocess.PIPE, stderr=subprocess.STDOUT, text=True, bufsize=1)
        for line in process.stdout:
            text_output.insert(tk.END, line)
            text_output.see(tk.END)
        process.stdout.close()
        process.wait()
        text_output.insert(tk.END, "\nCapture finished.\n")

    threading.Thread(target=run_ffmpeg, daemon=True).start()

# GUI setup
root = tk.Tk()
root.title("FFv1 Video Capture to MKV")

# Filename input
tk.Label(root, text="Enter the UUID:").pack(pady=(10, 2))
entry = tk.Entry(root, width=40)
entry.pack(pady=2)

# Start button
start_button = tk.Button(root, text="Start Capture", command=start_capture)
start_button.pack(pady=10)

# Console output
text_output = scrolledtext.ScrolledText(root, height=20, width=100)
text_output.pack(padx=10, pady=(5, 10))

root.mainloop()
