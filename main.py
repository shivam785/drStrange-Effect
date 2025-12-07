import cv2
import time
import mediapipe as mp

# ================== SETUP ==================
mpHands = mp.solutions.hands
hands = mpHands.Hands(
    static_image_mode=False,
    max_num_hands=2,  # <-- allow up to 2 hands
    min_detection_confidence=0.5,
    min_tracking_confidence=0.5
)
mpDraw = mp.solutions.drawing_utils

video = cv2.VideoCapture(0)

# Use property constants for clarity
video.set(cv2.CAP_PROP_FRAME_WIDTH, 1000)
video.set(cv2.CAP_PROP_FRAME_HEIGHT, 780)

# Load images with alpha channel
img_1 = cv2.imread('magic_circles/magic_circle_2.png', cv2.IMREAD_UNCHANGED)
img_2 = cv2.imread('magic_circles/magic_circle_cw.png', cv2.IMREAD_UNCHANGED)

deg = 0

# ================== UTIL FUNCTIONS ==================
def position_data(lmlist):
    global wrist, thumb_tip, index_mcp, index_tip, midle_mcp, midle_tip, ring_tip, pinky_tip
    wrist      = (lmlist[0][0],  lmlist[0][1])
    thumb_tip  = (lmlist[4][0],  lmlist[4][1])
    index_mcp  = (lmlist[5][0],  lmlist[5][1])
    index_tip  = (lmlist[8][0],  lmlist[8][1])
    midle_mcp  = (lmlist[9][0],  lmlist[9][1])
    midle_tip  = (lmlist[12][0], lmlist[12][1])
    ring_tip   = (lmlist[16][0], lmlist[16][1])
    pinky_tip  = (lmlist[20][0], lmlist[20][1])


def draw_line(p1, p2, size=5):
    # Red with white inner line
    cv2.line(img, p1, p2, (50, 50, 255), size)
    cv2.line(img, p1, p2, (255, 255, 255), max(1, round(size / 2)))


def calculate_distance(p1, p2):
    x1, y1, x2, y2 = p1[0], p1[1], p2[0], p2[1]
    length = ((x2 - x1) ** 2 + (y2 - y1) ** 2) ** 0.5
    return length


def transparent(base_img, targetImg, x, y, size=None):
    """Overlay RGBA targetImg on base_img at (x, y) with optional resize."""
    if targetImg is None:
        return base_img

    if size is not None:
        targetImg = cv2.resize(targetImg, size)

    newFrame = base_img.copy()

    # Split channels
    b, g, r, a = cv2.split(targetImg)
    overlay_color = cv2.merge((b, g, r))

    # Smooth the alpha mask a bit (kernel size 1 = no change, but keep for future tweaks)
    mask = cv2.medianBlur(a, 1)

    h, w, _ = overlay_color.shape
    h_base, w_base, _ = newFrame.shape

    # Bounds check for ROI
    if x < 0:
        x = 0
    if y < 0:
        y = 0
    if x + w > w_base or y + h > h_base:
        # Clip overlay if it's going out of frame
        w = min(w, w_base - x)
        h = min(h, h_base - y)
        overlay_color = overlay_color[0:h, 0:w]
        mask = mask[0:h, 0:w]

    if w <= 0 or h <= 0:
        return newFrame

    roi = newFrame[y:y + h, x:x + w]

    img1_bg = cv2.bitwise_and(roi.copy(), roi.copy(), mask=cv2.bitwise_not(mask))
    img2_fg = cv2.bitwise_and(overlay_color, overlay_color, mask=mask)
    newFrame[y:y + h, x:x + w] = cv2.add(img1_bg, img2_fg)

    return newFrame

# ================== MAIN LOOP ==================
prev_time = time.time()

while True:
    ret, img = video.read()
    if not ret:
        break

    img = cv2.flip(img, 1)
    h, w, c = img.shape

    rgbimg = cv2.cvtColor(img, cv2.COLOR_BGR2RGB)
    result = hands.process(rgbimg)

    if result.multi_hand_landmarks:
        for hand_landmarks in result.multi_hand_landmarks:
            lmList = []
            for lm in hand_landmarks.landmark:
                coorx, coory = int(lm.x * w), int(lm.y * h)
                lmList.append([coorx, coory])

            if len(lmList) >= 21:
                position_data(lmList)

                palm = calculate_distance(wrist, index_mcp)
                distance = calculate_distance(index_tip, pinky_tip)

                if palm == 0:  # Avoid division by zero
                    ratio = 0
                else:
                    ratio = distance / palm

                # Finger-web drawing state
                if 0.5 < ratio < 1.3:
                    draw_line(wrist, thumb_tip)
                    draw_line(wrist, index_tip)
                    draw_line(wrist, midle_tip)
                    draw_line(wrist, ring_tip)
                    draw_line(wrist, pinky_tip)

                    draw_line(thumb_tip, index_tip)
                    draw_line(thumb_tip, midle_tip)
                    draw_line(thumb_tip, ring_tip)
                    draw_line(thumb_tip, pinky_tip)

                # Magic circle state
                elif ratio >= 1.3:
                    centerx = midle_mcp[0]
                    centery = midle_mcp[1]

                    shield_size_factor = 3.0
                    diameter = round(palm * shield_size_factor)

                    x1 = round(centerx - (diameter / 2))
                    y1 = round(centery - (diameter / 2))

                    # Boundaries
                    if x1 < 0:
                        x1 = 0
                    elif x1 > w:
                        x1 = w

                    if y1 < 0:
                        y1 = 0
                    elif y1 > h:
                        y1 = h

                    if x1 + diameter > w:
                        diameter = w - x1
                    if y1 + diameter > h:
                        diameter = h - y1

                    if diameter > 0:
                        shield_size = (diameter, diameter)

                        # Rotation update
                        ang_vel = 2.0
                        deg = (deg + ang_vel) % 360

                        hei1, wid1, _ = img_1.shape
                        cen = (wid1 // 2, hei1 // 2)

                        M1 = cv2.getRotationMatrix2D(cen, round(deg), 1.0)
                        M2 = cv2.getRotationMatrix2D(cen, round(360 - deg), 1.0)

                        rotated1 = cv2.warpAffine(img_1, M1, (wid1, hei1))
                        rotated2 = cv2.warpAffine(img_2, M2, (wid1, hei1))

                        img = transparent(img, rotated1, x1, y1, shield_size)
                        img = transparent(img, rotated2, x1, y1, shield_size)

    # ================== FPS CALCULATION & DISPLAY ==================
    curr_time = time.time()
    fps = 1.0 / (curr_time - prev_time) if curr_time != prev_time else 0
    prev_time = curr_time

    cv2.putText(
        img,
        f"FPS: {int(fps)}",
        (10, 40),
        cv2.FONT_HERSHEY_SIMPLEX,
        1,
        (0, 255, 0),
        2
    )

    cv2.imshow("Image", img)
    k = cv2.waitKey(1) & 0xFF
    if k == ord('q'):
        break

video.release()
cv2.destroyAllWindows()
