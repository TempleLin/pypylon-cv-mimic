# basler-cv

`basler-cv` wraps the **pypylon** SDK so a Basler industrial camera behaves like `cv2.VideoCapture`.

```python
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
```

## Usage Installation

```bash
pip install git+https://github.com/TempleLin/pypylon-cv-mimic.git
```

## Development Installation (editable)

```bash
git clone https://github.com/TempleLin/pypylon-cv-mimic.git
cd basler-cv
pip install -e .
```

## Why?

* Hides the verbose Pylon API
* Consistent with OpenCV code you already write
* Supports monochrome and Bayer sensors out‑of‑the‑box
