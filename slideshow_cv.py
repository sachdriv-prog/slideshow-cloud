import cv2
import numpy as np
from PIL import Image
import os
import random
import sys

# --- SETTINGS ---
image_folder = "images"
# Argument se output filename lenge, default "slideshow.mp4" rahega
output_file = sys.argv[1] if len(sys.argv) > 1 else "slideshow.mp4"
seconds_per_image = 5
fps = 30
video_size = (1920, 1080)

cv2.setUseOptimized(True)
cv2.setNumThreads(8)

def load_and_resize(path, size):
    img = Image.open(path).convert("RGB")
    img = img.resize(size, Image.LANCZOS)
    return np.array(img)[:, :, ::-1]

def create_slide(img, direction, secs, fps, size):
    frames = []
    w, h = size
    move_x = int(w * 0.1)
    move_y = int(h * 0.1)
    total_frames = secs * fps

    for i in range(total_frames):
        alpha = i / total_frames
        dx, dy = 0, 0

        if direction == "left":
            dx = int(-move_x * alpha)
        elif direction == "right":
            dx = int(move_x * alpha)
        elif direction == "up":
            dy = int(-move_y * alpha)
        elif direction == "down":
            dy = int(move_y * alpha)

        M = np.float32([[1, 0, dx], [0, 1, dy]])
        frame = cv2.warpAffine(img, M, (w, h))
        frames.append(frame)

    return frames

# --- MAIN ---
# Subfolders se bhi images nikalne ke liye os.walk use kiya hai
images = []
for root, dirs, files in os.walk(image_folder):
    for f in files:
        if f.lower().endswith((".jpg", ".png", ".jpeg")):
            images.append(os.path.join(root, f))

random.shuffle(images)  # Har worker apni alag sequence banayega

fourcc = cv2.VideoWriter_fourcc(*"mp4v")
video = cv2.VideoWriter(output_file, fourcc, fps, video_size)

directions = ["left", "right", "up", "down"]

print(f"🎬 Starting random slideshow ({len(images)} images) for {output_file}...")

for img_path in images:
    print(f"🖼️ Processing {os.path.basename(img_path)}...")
    try:
        frame_img = load_and_resize(img_path, video_size)
        direction = random.choice(directions)
        frames = create_slide(frame_img, direction, seconds_per_image, fps, video_size)
        for f in frames:
            video.write(f)
    except Exception as e:
        print(f"⚠️ Error processing {img_path}: {e}")

video.release()
print(f"✅ Done! Saved as {output_file}")
