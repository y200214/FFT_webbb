# app/views/video_view.py

import tkinter as tk
from tkinter import ttk
from PIL import Image, ImageTk
import numpy as np

class VideoView(ttk.Frame):
    def __init__(self, parent, controller):
        super().__init__(parent)
        self.controller = controller
        
        self.video_label = ttk.Label(self)
        self.video_label.pack(fill=tk.BOTH, expand=True)

    def update_frame(self, frame_bgr):
        """
        OpenCVのフレーム(BGR形式)を受け取り、画面に表示する。
        """
        if frame_bgr is None:
            return
            
        # BGRからRGBに変換
        frame_rgb = frame_bgr[:, :, ::-1]
        
        # PIL Imageに変換
        pil_image = Image.fromarray(frame_rgb)
        
        # Tkinterで表示できる形式に変換
        imgtk = ImageTk.PhotoImage(image=pil_image)
        
        # ラベルに画像を設定
        self.video_label.imgtk = imgtk
        self.video_label.configure(image=imgtk)