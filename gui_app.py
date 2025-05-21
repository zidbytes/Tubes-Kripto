# gui_app.py
import tkinter as tk
from tkinter import filedialog, messagebox
import embed
import extract
import time


class StegoApp:
    def __init__(self, root):
        self.root = root
        self.root.title("Video Steganography with AES + SVD")
        self.create_widgets()

    def create_widgets(self):
        self.video_path = tk.StringVar()
        self.watermark_path = tk.StringVar()
        self.output_dir = tk.StringVar()

        tk.Label(self.root, text="Video File:").grid(row=0, column=0, sticky="e")
        tk.Entry(self.root, textvariable=self.video_path, width=40).grid(row=0, column=1)
        tk.Button(self.root, text="Browse", command=self.select_video).grid(row=0, column=2)

        tk.Label(self.root, text="Watermark Image:").grid(row=1, column=0, sticky="e")
        tk.Entry(self.root, textvariable=self.watermark_path, width=40).grid(row=1, column=1)
        tk.Button(self.root, text="Browse", command=self.select_watermark).grid(row=1, column=2)

        tk.Label(self.root, text="Output Folder:").grid(row=2, column=0, sticky="e")
        tk.Entry(self.root, textvariable=self.output_dir, width=40).grid(row=2, column=1)
        tk.Button(self.root, text="Browse", command=self.select_output_dir).grid(row=2, column=2)

        tk.Button(self.root, text="Embed Watermark", command=self.run_embed).grid(row=3, column=1, pady=5)
        tk.Button(self.root, text="Extract Watermark", command=self.run_extract).grid(row=4, column=1, pady=5)

    def select_video(self):
        path = filedialog.askopenfilename(filetypes=[("MP4 files", "*.mp4")])
        if path: self.video_path.set(path)

    def select_watermark(self):
        path = filedialog.askopenfilename(filetypes=[("Image files", "*.jpg *.png")])
        if path: self.watermark_path.set(path)

    def select_output_dir(self):
        path = filedialog.askdirectory()
        if path: self.output_dir.set(path)

    def run_embed(self):
        try:
            start = time.time()
            embed.embed_watermark(
                self.video_path.get(),
                self.watermark_path.get(),
                self.output_dir.get()
            )
            end = time.time()
            duration = end - start

            messagebox.showinfo("Success", f"✅ Watermark berhasil disisipkan.\n🕒 Waktu eksekusi: {duration:.2f} detik")
        except Exception as e:
            messagebox.showerror("Error", str(e))

    def run_extract(self):
        try:
            start = time.time()
            recovered_path, match = extract.extract_and_decrypt(self.output_dir.get())
            end = time.time()
            duration = end - start

            msg = "✅ Berhasil ekstrak & dekripsi watermark."

            messagebox.showinfo("Extraction Done", msg + f"\nFile: {recovered_path}")
        except Exception as e:
            messagebox.showerror("Error", str(e))

if __name__ == "__main__":
    root = tk.Tk()
    app = StegoApp(root)
    root.mainloop()
