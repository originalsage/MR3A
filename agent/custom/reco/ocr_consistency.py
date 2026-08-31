# -*- coding: utf-8 -*-
"""对两个 ROI 分别 OCR，仅当两者识别结果一致时才命中的 CustomRecognition。"""

from __future__ import annotations

from typing import List, Optional, Union

from maa.agent.agent_server import AgentServer
from maa.context import Context
from maa.custom_recognition import CustomRecognition
from maa.define import OCRResult, RecognitionDetail, RectType
from maa.pipeline import JOCR, JRecognitionType

from custom.pipeline_params import parse_pipeline_json_param
from utils.logger import logger
from utils.text_match import normalize_text


def _parse_roi(value, name: str) -> Optional[List[int]]:
    """解析 ROI 参数为 [x, y, w, h]，非法则返回 None。"""
    if not isinstance(value, (list, tuple)) or len(value) != 4:
        logger.error(f"OcrConsistency: 无效的 {name} 参数（需 [x, y, w, h]）: {value!r}")
        return None
    try:
        roi = [int(v) for v in value]
    except (TypeError, ValueError):
        logger.error(f"OcrConsistency: {name} 参数无法转为整数: {value!r}")
        return None
    if roi[2] <= 0 or roi[3] <= 0:
        logger.error(f"OcrConsistency: {name} 宽高须大于 0: {roi}")
        return None
    return roi


def _collect_text(detail: Optional[RecognitionDetail]) -> str:
    """从 OCR 识别详情中按顺序拼接所有文本。"""
    if detail is None:
        return ""
    results = detail.filtered_results or detail.all_results
    parts: List[str] = []
    for r in results:
        if isinstance(r, OCRResult) and r.text:
            parts.append(r.text.strip())
    return "".join(parts)


@AgentServer.custom_recognition("OcrConsistency")
class OcrConsistency(CustomRecognition):
    """
    对两个 ROI 分别做一次 OCR，仅当两个区域的识别结果一致时才命中。

    参数格式:
    {
        "roi_a": [x, y, w, h],
        "roi_b": [x, y, w, h],
        "threshold": 0.3,
        "strict": false,
        "return_box": "a"
    }

    字段说明:
    - roi_a: 第一个 OCR 区域，必填，格式 [x, y, w, h]。
    - roi_b: 第二个 OCR 区域，必填，格式 [x, y, w, h]。
    - threshold: OCR 阈值，可选，默认 0.3。
    - strict: 是否严格比较，可选，默认 false。
      - false: 规范化后比较（去标点/空白、大小写归一），对 OCR 细微差异更鲁棒。
      - true: 仅 strip 首尾空白后直接比较，要求完全一致。
    - return_box: 命中后返回的 ROI，可选，默认 "a"。
      - "a": 返回 roi_a
      - "b": 返回 roi_b
      - "union": 返回 roi_a 与 roi_b 的并集
    """

    def analyze(
        self,
        context: Context,
        argv: CustomRecognition.AnalyzeArg,
    ) -> Union[CustomRecognition.AnalyzeResult, Optional[RectType]]:
        try:
            param = parse_pipeline_json_param(argv.custom_recognition_param)

            roi_a = _parse_roi(param.get("roi_a"), "roi_a")
            roi_b = _parse_roi(param.get("roi_b"), "roi_b")
            if roi_a is None or roi_b is None:
                return None

            img = argv.image
            if img is None:
                logger.debug("OcrConsistency: 无截图，跳过")
                return None

            threshold = float(param.get("threshold", 0.3))
            strict = bool(param.get("strict", False))
            return_box = str(param.get("return_box", "a")).lower()

            text_a = self._ocr_text(context, img, roi_a, threshold)
            text_b = self._ocr_text(context, img, roi_b, threshold)

            if not text_a or not text_b:
                logger.debug(
                    f"OcrConsistency: OCR 结果为空 a={text_a!r} b={text_b!r}"
                )
                return None

            if strict:
                matched = text_a.strip() == text_b.strip()
            else:
                matched = normalize_text(text_a) == normalize_text(text_b)

            if not matched:
                logger.debug(f"OcrConsistency: 不一致 a={text_a!r} b={text_b!r}")
                return None

            box = self._resolve_return_box(roi_a, roi_b, return_box)
            logger.debug(f"OcrConsistency: 命中 text={text_a!r} box={box}")
            return CustomRecognition.AnalyzeResult(
                box=box,
                detail={"text_a": text_a, "text_b": text_b, "matched": text_a},
            )
        except Exception as e:
            logger.exception(f"OcrConsistency 执行出错: {e}")
            return None

    def _ocr_text(
        self,
        context: Context,
        img,
        roi: List[int],
        threshold: float,
    ) -> str:
        try:
            detail = context.run_recognition_direct(
                JRecognitionType.OCR,
                JOCR(roi=roi, threshold=threshold),
                img,
            )
        except Exception as e:
            logger.warning(f"OcrConsistency: OCR 执行失败 roi={roi}: {e}")
            return ""
        return _collect_text(detail)

    @staticmethod
    def _resolve_return_box(
        roi_a: List[int],
        roi_b: List[int],
        return_box: str,
    ) -> List[int]:
        if return_box == "b":
            return roi_b
        if return_box == "union":
            x1, y1, w1, h1 = roi_a
            x2, y2, w2, h2 = roi_b
            left = min(x1, x2)
            top = min(y1, y2)
            right = max(x1 + w1, x2 + w2)
            bottom = max(y1 + h1, y2 + h2)
            return [left, top, right - left, bottom - top]
        return roi_a
