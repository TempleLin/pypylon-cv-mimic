"""Camera abstraction that mimics cv2.VideoCapture."""

import cv2
from pypylon import pylon

_BAYER_TO_CVT = {
    "BayerRG8": cv2.COLOR_BAYER_RG2RGB,
    "BayerBG8": cv2.COLOR_BAYER_BG2RGB,
    "BayerGR8": cv2.COLOR_BAYER_GR2RGB,
    "BayerGB8": cv2.COLOR_BAYER_GB2RGB,
}

class BaslerCamera:
    """Context‑manager style Basler camera.

    Parameters
    ----------
    pixel_format : str, default "Mono8"
        Any Pylon pixel format like 'Mono8', 'BayerRG8', etc.
    exposure_time : int | None
        Exposure in micro‑seconds (e.g. 16_700 for 16.7 ms).
    frame_rate : float | None
        Target FPS. Camera must support frame‑rate control.
    resize : tuple[int, int] | None
        (width, height) to resize frames on the fly.
    timeout_ms : int
        Retrieve timeout.
    """

    def __init__(
        self,
        index: int = 0,
        *,
        pixel_format: str = "Mono8",
        exposure_time: int | None = None,
        frame_rate: float | None = None,
        resize: tuple[int, int] | None = None,
        timeout_ms: int = 5000,
    ) -> None:
        self._index = index
        self._pixel_format = pixel_format
        self._exposure_time = exposure_time
        self._frame_rate = frame_rate
        self._resize = resize
        self._timeout = timeout_ms

        self._camera = None

    # ------------------------------------------------------------------ #
    # Public API – mirrors cv2.VideoCapture
    # ------------------------------------------------------------------ #

    def open(self) -> None:
        if self._camera:
            return

        self._camera = pylon.InstantCamera(
            pylon.TlFactory.GetInstance().CreateFirstDevice()
        )
        self._camera.Open()

        # Pixel format
        if self._pixel_format:
            self._camera.PixelFormat.SetValue(self._pixel_format)

        # Exposure
        if self._exposure_time is not None:
            self._camera.ExposureTime.SetValue(self._exposure_time)

        # Frame rate
        if self._frame_rate is not None:
            self._camera.AcquisitionFrameRateEnable.SetValue(True)
            self._camera.AcquisitionFrameRate.SetValue(self._frame_rate)

        self._camera.StartGrabbing(pylon.GrabStrategy_LatestImageOnly)

    def isOpened(self) -> bool:  # noqa: N802 (mimic cv2 naming)
        return self._camera is not None

    def read(self):
        """Return (success, frame) just like cv2.VideoCapture.read."""
        if not self.isOpened():
            self.open()

        if not self._camera.IsGrabbing():
            return False, None

        grab = self._camera.RetrieveResult(self._timeout, pylon.TimeoutHandling_ThrowException)
        try:
            if not grab.GrabSucceeded():
                return False, None

            frame = grab.Array

            # Color conversion for Bayer
            if self._pixel_format in _BAYER_TO_CVT:
                frame = cv2.cvtColor(frame, _BAYER_TO_CVT[self._pixel_format])

            if self._resize:
                frame = cv2.resize(frame, self._resize, interpolation=cv2.INTER_LINEAR)

            return True, frame
        finally:
            grab.Release()

    def release(self) -> None:
        if self._camera:
            self._camera.StopGrabbing()
            self._camera.Close()
            self._camera = None

    # ------------------------------------------------------------------ #
    # Pythonic niceties
    # ------------------------------------------------------------------ #

    def __enter__(self):
        self.open()
        return self

    def __exit__(self, exc_type, exc, tb):
        self.release()
