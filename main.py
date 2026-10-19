# -*- coding: utf-8 -*-
"""轻量化人脸考勤打卡系统（个人练习项目）。

流程：实时采集画面 -> 灰度转换 + 高斯模糊降噪 -> Haar 级联人脸检测
-> 一键打卡写入本地文本。

注意：本程序只检测画面中是否存在人脸，不进行身份识别或活体检测。
"""

import datetime
import tkinter as tk
from tkinter import ttk

import cv2
import numpy as np
from PIL import Image, ImageTk


RECORD_FILE = "attendance_records.txt"
CASCADE_PATH = cv2.data.haarcascades + "haarcascade_frontalface_default.xml"
CAMERA_INDICES = (0, 1)
SIMULATED_IMAGE = "test.jpg"


face_cascade = cv2.CascadeClassifier(CASCADE_PATH)
if face_cascade.empty():
    raise RuntimeError("Haar 级联分类器加载失败：" + CASCADE_PATH)


def init_video_source():
    """优先打开真实摄像头，失败则尝试本地图片模拟。"""
    for idx in CAMERA_INDICES:
        cap = cv2.VideoCapture(idx)
        if cap.isOpened():
            return cap, "摄像头 #%d" % idx

    cap = cv2.VideoCapture(SIMULATED_IMAGE)
    if cap.isOpened():
        return cap, "模拟源：%s" % SIMULATED_IMAGE

    return None, None


def make_simulated_frame():
    """视频源全部不可用时生成提示画面。"""
    frame = np.full((480, 640, 3), 48, dtype=np.uint8)
    cv2.putText(
        frame,
        "No video source available",
        (90, 240),
        cv2.FONT_HERSHEY_SIMPLEX,
        0.9,
        (255, 255, 255),
        2,
    )
    cv2.putText(
        frame,
        "Put a face photo as test.jpg",
        (110, 280),
        cv2.FONT_HERSHEY_SIMPLEX,
        0.7,
        (180, 180, 180),
        2,
    )
    return frame


def preprocess(frame):
    """执行灰度转换与高斯模糊，返回单通道图像。"""
    gray = cv2.cvtColor(frame, cv2.COLOR_BGR2GRAY)
    return cv2.GaussianBlur(gray, (5, 5), 0)


def detect_faces(gray):
    """使用 Haar 级联分类器检测正面人脸。"""
    return face_cascade.detectMultiScale(
        gray,
        scaleFactor=1.1,
        minNeighbors=5,
        minSize=(80, 80),
    )


def annotate(frame, faces):
    """在画面中绘制人脸检测框。"""
    for x, y, w, h in faces:
        cv2.rectangle(frame, (x, y), (x + w, y + h), (0, 255, 0), 2)
        cv2.putText(
            frame,
            "face",
            (x, max(y - 8, 16)),
            cv2.FONT_HERSHEY_SIMPLEX,
            0.6,
            (0, 255, 0),
            2,
        )
    return frame


def write_record(name):
    """将姓名和打卡时间追加到本地记录文件。"""
    timestamp = datetime.datetime.now().strftime("%Y-%m-%d %H:%M:%S")
    line = "%s,%s" % (name, timestamp)
    with open(RECORD_FILE, "a", encoding="utf-8") as file:
        file.write(line + "\n")
    return line


class AttendanceApp:
    UPDATE_INTERVAL_MS = 30

    def __init__(self, root):
        self.root = root
        root.title("轻量化人脸考勤打卡系统")

        self.cap, self.source_desc = init_video_source()
        self.latest_frame = None
        self.latest_faces = []
        self._photo = None

        self._build_ui()
        self._update_loop()

    def _build_ui(self):
        self.video_label = tk.Label(self.root, bg="black")
        self.video_label.pack(side="left", padx=10, pady=10)

        panel = ttk.Frame(self.root)
        panel.pack(side="right", fill="y", padx=15, pady=15)

        source_text = self.source_desc or "不可用"
        ttk.Label(panel, text="视频源：%s" % source_text).pack(anchor="w")
        ttk.Label(panel, text="姓名：").pack(anchor="w", pady=(15, 0))

        self.name_entry = ttk.Entry(panel, width=20)
        self.name_entry.pack(anchor="w", pady=(2, 10))

        self.checkin_btn = ttk.Button(panel, text="打 卡", command=self.on_checkin)
        self.checkin_btn.pack(anchor="w", pady=(0, 15))

        self.face_count_label = ttk.Label(panel, text="检测到 0 张人脸")
        self.face_count_label.pack(anchor="w")

        self.status_label = tk.Label(
            panel,
            text="等待打卡…",
            fg="gray",
            wraplength=240,
            justify="left",
        )
        self.status_label.pack(anchor="w", pady=(15, 0), fill="x")

        ttk.Button(panel, text="退出", command=self.root.destroy).pack(
            anchor="w", pady=(20, 0)
        )

    def _grab_frame(self):
        if self.cap is None:
            return make_simulated_frame()

        ok, frame = self.cap.read()
        return frame if ok else make_simulated_frame()

    def _update_loop(self):
        frame = self._grab_frame()
        gray = preprocess(frame)
        faces = detect_faces(gray)

        self.latest_frame = frame
        self.latest_faces = faces
        self.face_count_label.configure(text="检测到 %d 张人脸" % len(faces))

        annotated = annotate(frame, faces)
        rgb = cv2.cvtColor(annotated, cv2.COLOR_BGR2RGB)
        image = Image.fromarray(rgb)
        self._photo = ImageTk.PhotoImage(image)
        self.video_label.configure(image=self._photo)

        self.root.after(self.UPDATE_INTERVAL_MS, self._update_loop)

    def on_checkin(self):
        name = self.name_entry.get().strip()

        if not name:
            self._set_status("请先输入姓名", "orange")
            return
        if self.latest_frame is None:
            self._set_status("画面未就绪，请稍候", "orange")
            return
        if len(self.latest_faces) == 0:
            self._set_status("未检测到人脸，打卡失败", "red")
            return

        line = write_record(name)
        self._set_status("打卡成功！%s" % line, "green")

    def _set_status(self, text, color):
        self.status_label.configure(text=text, fg=color)


def main():
    root = tk.Tk()
    app = AttendanceApp(root)
    root.mainloop()

    if app.cap is not None:
        app.cap.release()


if __name__ == "__main__":
    main()
