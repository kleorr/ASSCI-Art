# 📸 ASCII Converter

A powerful and fast desktop application to transform images and videos into stylized ASCII art. Built with Python and optimized for performance.

## 🚀 Key Features

* **Fast Video Rendering**: Optimized engine that processes hundreds of frames in seconds.
* **Audio Support**: Automatically merges original audio with the generated ASCII video.
* **Real-time Preview**: Adjust the "Width" slider to see instant changes in detail density.
* **Social Media Ready**: Unique "Copy as Markdown" feature for perfect pasting into Discord or Telegram.
* **Standalone EXE**: No Python installation required – just download and run.

## 🛠 Tech Stack

* **GUI**: CustomTkinter (Modern Dark Theme)
<img width="867" height="990" alt="image" src="https://github.com/user-attachments/assets/0093ae5c-7979-4f8f-bfd8-9af8425cb4d6" />
* **Image Processing**: OpenCV & Pillow (PIL)
<img width="1244" height="1685" alt="epng" src="https://github.com/user-attachments/assets/9e4aabb4-8953-4c23-9f60-e3bfd04ff1da" />
* **Video Processing**: MoviePy 2.0+ & ImageIO
![Adobe Express - bad apple (online-video-cutter com)](https://github.com/user-attachments/assets/d5d2aec0-38be-42d8-b8b9-1f841ddd0489)

## 📖 How to Use

1.  **Select File**: Upload any image (.png, .jpg) or video (.mp4, .avi).
2.  **Adjust Detail**: Use the slider to change the character width (lower for retro look, higher for detail).
3.  **Export**: 
    * Click **"Save as PNG"** for a static image.
    * Click **"Copy as Markdown"** to share the text version.
    * Click **"Render ASCII Video"** to create a full MP4 with sound.

    ## 📦 Installation (for Developers)

1. Clone the repository:
```git clone https://github.com/your-username/ascii-studio-pro.git```

2. Install dependencies:
```pip install customtkinter Pillow opencv-python moviepy proglog imageio imageio-ffmpeg```

3. Run the script:
```python main.py```
