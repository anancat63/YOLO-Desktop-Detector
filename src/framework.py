from __future__ import annotations

from dataclasses import dataclass
from typing import Any, Dict, List

import numpy as np
import torch
from ultralytics import YOLO

from . import config as Config


@dataclass
class DetectionResult:
    raw: Any
    locations: List[List[int]]
    classes: List[int]
    confidences: List[str]
    ids: List[int]
    plot: np.ndarray


class DetectorFramework:
    def __init__(self):
        cfg = Config.get_detection_config()

        model_path_cfg = cfg["model_path"]
        if model_path_cfg.endswith(".pt") and ("/" in model_path_cfg or "\\" in model_path_cfg):
            self.model_path = Config.resolve_path(model_path_cfg)
        else:
            self.model_path = model_path_cfg

        self.task = cfg["task"]
        self.default_conf = cfg["conf"]
        self.default_iou = cfg["iou"]
        self.device = self._resolve_device(cfg["device"])

        self.model = YOLO(self.model_path, task=self.task)
        self._warmup(cfg.get("warmup_shape", [48, 48, 3]))

    @staticmethod
    def _resolve_device(config_device: str):
        if str(config_device).lower() == "auto":
            return 0 if torch.cuda.is_available() else "cpu"
        return config_device

    def _warmup(self, warmup_shape: Any) -> None:
        if not (isinstance(warmup_shape, list) and len(warmup_shape) == 3):
            return
        warmup_img = np.zeros(tuple(warmup_shape), dtype=np.uint8)
        self.model(warmup_img, device=self.device, verbose=False)

    def predict(self, source: Any, conf: float | None = None, iou: float | None = None) -> Dict[str, Any]:
        conf_val = self.default_conf if conf is None else float(conf)
        iou_val = self.default_iou if iou is None else float(iou)

        results = self.model(source, conf=conf_val, iou=iou_val, device=self.device, verbose=False)
        result = results[0]
        parsed = self.parse_result(result)
        return {
            "raw": parsed.raw,
            "locations": parsed.locations,
            "classes": parsed.classes,
            "confidences": parsed.confidences,
            "ids": parsed.ids,
            "plot": parsed.plot,
        }

    @staticmethod
    def parse_result(result: Any) -> DetectionResult:
        if result.boxes is None or len(result.boxes) == 0:
            return DetectionResult(raw=result, locations=[], classes=[], confidences=[], ids=[], plot=result.plot())

        locations = [list(map(int, box)) for box in result.boxes.xyxy.tolist()]
        classes = [int(cls_id) for cls_id in result.boxes.cls.tolist()]
        confidences = [f"{float(score) * 100:.2f} %" for score in result.boxes.conf.tolist()]
        ids = list(range(len(locations)))

        return DetectionResult(
            raw=result,
            locations=locations,
            classes=classes,
            confidences=confidences,
            ids=ids,
            plot=result.plot(),
        )
