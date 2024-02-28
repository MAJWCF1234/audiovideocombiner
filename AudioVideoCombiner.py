import tkinter as tk
from tkinter import filedialog, messagebox, ttk
import subprocess
import threading
import os

class AVCombinerApp:
    def __init__(self, root):
        self.root = root
        self.root.title("Audio Video Combiner")
        self.root.geometry("600x400")

        self.audio_files = []
        self.video_file = ""
        self.output_video_path = ""

        self.progress_label = tk.Label(self.root, text="Ready")
        self.progress = ttk.Progressbar(self.root, orient=tk.HORIZONTAL, length=100, mode='determinate')
        self.create_widgets()

    def create_widgets(self):
        self.audio_files_label = tk.Label(self.root, text="No Audio Files Selected", wraplength=550)
        self.audio_files_label.grid(row=0, column=0, columnspan=2, padx=10, pady=5, sticky="w")

        self.video_file_label = tk.Label(self.root, text="No Video File Selected", wraplength=550)
        self.video_file_label.grid(row=1, column=0, columnspan=2, padx=10, pady=5, sticky="w")

        self.browse_audio_button = tk.Button(self.root, text="Select Audio Files", command=self.select_audio_files)
        self.browse_audio_button.grid(row=2, column=0, padx=10, pady=5, sticky="ew")

        self.browse_video_button = tk.Button(self.root, text="Select Video File", command=self.select_video_file)
        self.browse_video_button.grid(row=2, column=1, padx=10, pady=5, sticky="ew")

        self.combine_button = tk.Button(self.root, text="Combine and Process", command=self.prepare_processing)
        self.combine_button.grid(row=3, column=0, columnspan=2, padx=10, pady=10, sticky="ew")

        self.progress_label.grid(row=4, column=0, columnspan=2, padx=10, pady=5, sticky="ew")
        self.progress.grid(row=5, column=0, columnspan=2, padx=10, pady=5, sticky="ew")

        self.root.grid_columnconfigure(0, weight=1)
        self.root.grid_columnconfigure(1, weight=1)

    def select_audio_files(self):
        self.audio_files = filedialog.askopenfilenames(title="Select Audio Files", filetypes=(("MP3 files", "*.mp3"),))
        if self.audio_files:
            self.audio_files_label.config(text=f"Selected {len(self.audio_files)} Audio File(s)")

    def select_video_file(self):
        self.video_file = filedialog.askopenfilename(title="Select a Video File", filetypes=(("MP4 files", "*.mp4"),))
        if self.video_file:
            self.video_file_label.config(text=f"Selected Video File: {os.path.basename(self.video_file)}")

    def prepare_processing(self):
        if not self.audio_files or not self.video_file:
            messagebox.showerror("Error", "Please select both audio and video files.")
            return
        
        self.output_video_path = filedialog.asksaveasfilename(defaultextension=".mp4", filetypes=[("MP4 files", "*.mp4")])
        if not self.output_video_path:
            messagebox.showinfo("Info", "Output file location was not selected. Processing cancelled.")
            return

        if os.path.exists(self.output_video_path):
            response = messagebox.askyesno("Confirm Overwrite", "Output file already exists. Do you want to overwrite it?")
            if not response:
                return
        
        self.disable_ui()
        self.progress_label.config(text="Processing...")
        self.progress.start(10)
        threading.Thread(target=self.process_files, daemon=True).start()

    def process_files(self):
        ffmpeg_path = "C:\\ffmpeg\\bin\\ffmpeg.exe"
        temp_list_path = "temp_list.txt"
        combined_audio = "combined_audio.mp3"
        
        try:
            with open(temp_list_path, "w") as f:
                for file in self.audio_files:
                    f.write(f"file '{file}'\n")
            
            subprocess.run([ffmpeg_path, "-f", "concat", "-safe", "0", "-i", temp_list_path, "-c", "copy", combined_audio], check=True)

            # Updated FFmpeg command to copy the video stream and truncate to fit the audio length
            subprocess.run([ffmpeg_path, "-stream_loop", "-1", "-i", self.video_file, "-i", combined_audio, "-shortest", "-map", "0:v:0", "-map", "1:a:0", "-c:v", "copy", "-c:a", "aac", "-strict", "experimental", self.output_video_path], check=True)
        except subprocess.CalledProcessError:
            self.root.after(0, messagebox.showerror, "Processing Error", "An error occurred during processing. Please check your FFmpeg path and files.")
        finally:
            if os.path.exists(temp_list_path):
                os.remove(temp_list_path)
            if os.path.exists(combined_audio):
                os.remove(combined_audio)
            self.finish_processing()

    def disable_ui(self):
        self.browse_audio_button.config(state="disabled")
        self.browse_video_button.config(state="disabled")
        self.combine_button.config(state="disabled")

    def enable_ui(self):
        self.browse_audio_button.config(state="normal")
        self.browse_video_button.config(state="normal")
        self.combine_button.config(state="normal")

    def update_progress(self, message):
        self.progress_label.config(text=message)

    def finish_processing(self):
        self.progress.stop()
        self.progress['value'] = 0
        self.enable_ui()
        self.progress_label.config(text="Ready")
        messagebox.showinfo("Success", "Process completed successfully. Output file is " + self.output_video_path)

if __name__ == "__main__":
    root = tk.Tk()
    app = AVCombinerApp(root)
    root.mainloop()
