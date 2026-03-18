import customtkinter as ctk
from PIL import Image, ImageDraw, ImageFont, ImageGrab
from tkinter import filedialog, messagebox
import tempfile
import os
import cv2
import numpy as np
import threading
import sys
import time
from moviepy import VideoFileClip, AudioFileClip

# Класс для перехвата консоли и вывода в GUI
class TextRedirector:
    def __init__(self, widget):
        self.widget = widget
    def write(self, str):
        self.widget.insert("end", str)
        self.widget.see("end")
    def flush(self):
        pass

class AsciiConverter(ctk.CTk):
    def __init__(self):
        super().__init__()

        self.title("ASCII Converter bykleorr")
        self.geometry("1100x950")

        self.grid_columnconfigure(0, weight=1)
        self.grid_rowconfigure(1, weight=1)

        self.chars = ["@", "#", "S", "%", "?", "*", "+", ";", ":", ",", "."]

        # Панель управления
        self.top_frame = ctk.CTkFrame(self)
        self.top_frame.grid(row=0, column=0, padx=20, pady=10, sticky="ew")

        # АНГЛИЙСКИЙ: Select File
        self.btn_open = ctk.CTkButton(self.top_frame, text="Select File", command=self.open_file)
        self.btn_open.pack(side="left", padx=10)

        self.width_slider = ctk.CTkSlider(self.top_frame, from_=50, to=250, command=self.update_ascii)
        self.width_slider.set(100)
        self.width_slider.pack(side="left", padx=10)

        # АНГЛИЙСКИЙ: Copy as Markdown (так правильнее для Discord/TG)
        self.btn_copy = ctk.CTkButton(self.top_frame, text="Copy as Markdown", fg_color="#b85c00", hover_color="#8f4700", command=self.copy_to_clipboard)
        self.btn_copy.pack(side="left", padx=5)

        # АНГЛИЙСКИЙ: Save as PNG
        self.btn_save_png = ctk.CTkButton(self.top_frame, text="Save as PNG", fg_color="darkgreen", command=self.save_as_png)
        self.btn_save_png.pack(side="left", padx=5)

        # АНГЛИЙСКИЙ: Render ASCII Video
        self.btn_video = ctk.CTkButton(self.top_frame, text="Render ASCII Video", fg_color="#1f538d", command=self.start_video_process, state="disabled")
        self.btn_video.pack(side="left", padx=5)

        # Основное поле просмотра
        self.text_area = ctk.CTkTextbox(self, font=("Consolas", 7), wrap="none")
        self.text_area.grid(row=1, column=0, padx=20, pady=(10, 0), sticky="nsew")

        # ОКНО ЛОГОВ
        self.log_area = ctk.CTkTextbox(self, height=100, font=("Consolas", 9), fg_color="#1a1a1a", text_color="#00ff00")
        self.log_area.grid(row=2, column=0, padx=20, pady=5, sticky="ew")
        self.log_area.insert("0.0", "--- System logs ---\n")

        # ПОЛОСКА ПРОГРЕССА
        self.progress = ctk.CTkProgressBar(self, orientation="horizontal", mode="determinate")
        self.progress.grid(row=3, column=0, padx=20, pady=10, sticky="ew")
        self.progress.set(0)

        self.current_path = None
        self.video_source = None
        self.ascii_result = ""

        # Перенаправляем stdout в наше окно логов
        sys.stdout = TextRedirector(self.log_area)

    def open_file(self):
        path = filedialog.askopenfilename()
        if path:
            self.current_path = path
            if path.lower().endswith(('.mp4', '.avi', '.mov')):
                self.btn_video.configure(state="normal")
                self.video_source = path
                cap = cv2.VideoCapture(path)
                ret, frame = cap.read()
                if ret:
                    temp_img = Image.fromarray(cv2.cvtColor(frame, cv2.COLOR_BGR2RGB))
                    temp_path = os.path.join(tempfile.gettempdir(), "preview.png")
                    temp_img.save(temp_path)
                    self.current_path = temp_path
                cap.release()
            else:
                self.btn_video.configure(state="disabled")
            self.update_ascii()

    def convert_to_ascii(self, img_obj, width):
        aspect_ratio = img_obj.height / img_obj.width
        new_height = int(aspect_ratio * width * 0.55)
        img = img_obj.resize((width, new_height)).convert("L")
        pixels = img.getdata()
        new_pixels = [self.chars[pixel // 25] if pixel // 25 < len(self.chars) else self.chars[-1] for pixel in pixels]
        return "\n".join(["".join(new_pixels[i:i+width]) for i in range(0, len(new_pixels), width)])

    def update_ascii(self, *args):
        if self.current_path:
            width = int(self.width_slider.get())
            img = Image.open(self.current_path)
            self.ascii_result = self.convert_to_ascii(img, width)
            self.text_area.delete("1.0", "end")
            self.text_area.insert("1.0", self.ascii_result)

    def copy_to_clipboard(self):
        if not self.ascii_result: return
        formatted_text = f"```text\n{self.ascii_result}\n```"
        self.clipboard_clear()
        self.clipboard_append(formatted_text)
        self.update() 
        messagebox.showinfo("Copied", "Text copied to clipboard successfully.")

    def _render_ascii_to_image(self, ascii_str):
        lines = ascii_str.split("\n")
        font_size = 15
        try: font = ImageFont.truetype("consola.ttf", font_size)
        except: font = ImageFont.load_default()
        char_w, char_h = 9, 15
        img = Image.new("RGB", (char_w * len(lines[0]) + 20, char_h * len(lines) + 20), color="#1e1e1e")
        draw = ImageDraw.Draw(img)
        for i, line in enumerate(lines):
            draw.text((10, 10 + i * char_h), line, fill="#cfcfcf", font=font)
        return img

    def start_video_process(self):
        self.log_area.delete("1.0", "end")
        print("[SYSTEM] Starting rendering thread...")
        threading.Thread(target=self.save_as_video, daemon=True).start()

    def save_as_video(self):
        save_path = filedialog.asksaveasfilename(defaultextension=".mp4")
        if not save_path: return

        self.btn_video.configure(state="disabled")
        width = int(self.width_slider.get())
        cap = cv2.VideoCapture(self.video_source)
        orig_fps = cap.get(cv2.CAP_PROP_FPS)
        total_frames = int(cap.get(cv2.CAP_PROP_FRAME_COUNT))
        
        temp_video = os.path.join(tempfile.gettempdir(), "temp_ascii.mp4")
        
        ret, frame = cap.read()
        if not ret: return
        
        sample_img = self._render_ascii_to_image(self.convert_to_ascii(Image.fromarray(frame), width))
        fourcc = cv2.VideoWriter_fourcc(*'mp4v')
        out = cv2.VideoWriter(temp_video, fourcc, orig_fps, sample_img.size)

        print(f"[1/2] Rendering frames (total: {total_frames})...")
        count = 0
        while cap.isOpened():
            ret, frame = cap.read()
            if not ret: break
            
            pil_img = Image.fromarray(cv2.cvtColor(frame, cv2.COLOR_BGR2RGB))
            ascii_frame = self.convert_to_ascii(pil_img, width)
            rendered = self._render_ascii_to_image(ascii_frame)
            out.write(cv2.cvtColor(np.array(rendered), cv2.COLOR_RGB2BGR))
            
            count += 1
            if count % 10 == 0:
                prog = (count / total_frames) * 0.7 
                self.progress.set(prog)
                self.update_idletasks()

        cap.release()
        out.release()

        # АНГЛИЙСКИЙ: Merging audio
        print("[2/2] Merging audio and rendering final video (this may take a moment)...")
        try:
            v_clip = VideoFileClip(temp_video)
            a_clip = AudioFileClip(self.video_source)
            final = v_clip.with_audio(a_clip).with_duration(v_clip.duration)
            
            # САМОЕ ВАЖНОЕ: logger=None
            final.write_videofile(save_path, fps=24, codec="libx264", audio_codec="aac", bitrate="2500k", logger=None)
            
            v_clip.close()
            a_clip.close()
            self.progress.set(1.0)
            print("\n[SUCCESS] Video rendered successfully!")
            messagebox.showinfo("Success", "Video rendered successfully!")
        except Exception as e:
            print(f"\n[ERROR] {e}")
            messagebox.showerror("Error Details", f"An error occurred:\n{e}")
        
        self.btn_video.configure(state="normal")
        
        # Безопасное удаление временного файла (чтобы не было PermissionError)
        def safe_delete():
            time.sleep(2)
            if os.path.exists(temp_video):
                try: os.remove(temp_video)
                except: pass
        threading.Thread(target=safe_delete, daemon=True).start()

    def save_as_png(self):
        if not self.ascii_result: return
        path = filedialog.asksaveasfilename(defaultextension=".png")
        if path:
            self._render_ascii_to_image(self.ascii_result).save(path)

if __name__ == "__main__":
    app = AsciiConverter()
    app.mainloop()
