import cv2
from basler_cv import BaslerCamera

with BaslerCamera(pixel_format="BayerRG8", exposure_time=16_700, frame_rate=21.0) as cap:
    while True:
        ok, frame = cap.read()
        if not ok:
            break
        cv2.imshow("Live", frame)
        if cv2.waitKey(1) == 27:  # ESC
            break
cv2.destroyAllWindows()
