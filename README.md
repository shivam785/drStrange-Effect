
# ⭐ DR strange effect

**© 2025 — All Rights Reserved**

---

## ⭐ Overview

Magic Circle Hand Tracking is a real-time, webcam-powered gesture VFX system using **MediaPipe** and **OpenCV**.

It detects hand spread distance and automatically summons rotating magic sigils exactly at the palm center — inspired by cinematic wizard spell visuals.

You can:

* ⭐ Track both hands simultaneously
* ⭐ Summon magic circles by opening your palm

---

## ⭐ Features

### 🖐 Dual-Hand Tracking

* Recognizes **two hands at once**
* Independent magic circle per hand
* Each hand triggers effects separately

### 🪄 Gesture-Activated Magic

* **Open palm** → rotating sigil summon
* **Partial spread** → glowing fingertip web lines
* Real-time auto rotation for aesthetic spell casting

### ⚡ Performance

* On-screen **FPS counter**
* Smooth alpha compositing
* Optimized overlay & detection pipeline

---

## ⭐ Requirements

* **Python 3.8+**
* A working **Webcam**
* PNG sigils with transparency (`RGBA`)

### Python Libraries

* mediapipe
* opencv-python
* numpy

📌 Install dependencies:

```bash
pip install opencv-python mediapipe numpy
```

---

## ⭐ Assets

Folder structure (required):

```
magic_circles/
│─ magic_circle_ccw.png   # rotates counter-clockwise  
│─ magic_circle_cw.png    # rotates clockwise  
```

Both must be **transparent PNGs** (no white box or artifacts).

---

## ⭐ Controls

| Key   | Action       |
| ----- | ------------ |
| **q** | Quit program |

Everything else is **gesture-controlled**:

* Spread palm → Summon circle
* Slight spread → Finger-web beam lines

---

## ⭐ Recording Advice

* Good lighting = best hand detection
* Keep full hand visible
* Avoid busy background

---

## ⭐ Advanced Tips

* Lower camera resolution for higher FPS
