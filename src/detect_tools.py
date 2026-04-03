from __future__ import annotations

import cv2
import numpy as np
from PySide6.QtGui import QImage, QPixmap


def img_cvread(path: str):
    """Read image with Chinese path support."""
    return cv2.imdecode(np.fromfile(path, dtype=np.uint8), cv2.IMREAD_COLOR)


def cvimg_to_qpiximg(cvimg: np.ndarray) -> QPixmap:
    """Convert OpenCV image(BGR/RGB/gray) to QPixmap."""
    if cvimg is None or cvimg.size == 0:
        return QPixmap()

    if len(cvimg.shape) == 2:
        cvimg = cv2.cvtColor(cvimg, cv2.COLOR_GRAY2RGB)
    else:
        cvimg = cv2.cvtColor(cvimg, cv2.COLOR_BGR2RGB)

    height, width, channel = cvimg.shape
    bytes_per_line = width * channel
    qimg = QImage(cvimg.data, width, height, bytes_per_line, QImage.Format_RGB888)
    return QPixmap.fromImage(qimg)
