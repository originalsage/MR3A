# -*- coding: utf-8 -*-
"""账号登录（折中版）：Agent 直接读取客户端实例配置里的明文账号密码并输入。

- 账号密码仍保存在 config/instances/*.json（客户端 UI 可编辑，明文）
- 但不再通过 option 的 pipeline_override 注入 task param，所以：
  - 客户端日志「任务管线合并」不含凭据
  - MaaFramework 日志只看到 {"field":"password"}
  - adb 进程命令行不含密码（stdin）
- Agent 日志只记录字段名和长度。
"""

from __future__ import annotations

import json
import subprocess

from maa.agent.agent_server import AgentServer
from maa.context import Context
from maa.custom_action import CustomAction

from utils import logger
from utils.runtime_paths import get_runtime_paths

FIELD_TO_KEY = {"account": "账号", "password": "密码"}


def _clean(text: str) -> bool:
    if not text or len(text) > 64 or not text.isascii():
        return False
    return all(0x21 <= ord(ch) <= 0x7E and ch != "'" for ch in text)


def _instance_files() -> list[dict]:
    root = get_runtime_paths().project_root
    instances_dir = root / "config" / "instances"
    active = None
    appsettings = root / "appsettings.json"
    if appsettings.is_file():
        try:
            active = json.loads(appsettings.read_text(encoding="utf-8")).get("Instances.LastActive")
        except Exception:
            active = None
    candidates = []
    if active:
        candidates.append(instances_dir / f"{active}.json")
    candidates.extend(sorted(instances_dir.glob("*.json")))
    out = []
    for p in candidates:
        if not p.is_file():
            continue
        try:
            out.append(json.loads(p.read_text(encoding="utf-8")))
        except Exception:
            logger.exception(f"SecureTextInput: 读取实例配置失败 {p}")
    return out


def _find_credentials() -> tuple[dict, dict | None]:
    """返回 (凭据 data, 该实例的 AdbDevice)。"""
    for inst in _instance_files():
        for task in inst.get("TaskItems", []):
            if task.get("name") != "启动游戏":
                continue
            for opt in task.get("option", []):
                if opt.get("name") != "请选择服务器":
                    continue
                for sub in opt.get("sub_options", []):
                    if sub.get("name") == "账号密码":
                        return sub.get("data") or {}, inst.get("AdbDevice") or {}
    return {}, None


def _send_via_adb(text: str, device: dict | None) -> bool:
    adb = (device or {}).get("AdbPath")
    serial = (device or {}).get("AdbSerial")
    if not adb or not serial:
        logger.error("SecureTextInput: 找不到 AdbPath/AdbSerial")
        return False
    result = subprocess.run(
        [adb, "-s", serial, "shell"],
        input=f"input text '{text}'\n",
        text=True,
        stdout=subprocess.DEVNULL,
        stderr=subprocess.DEVNULL,
        timeout=20,
        creationflags=0x08000000,
    )
    return result.returncode == 0


@AgentServer.custom_action("SecureTextInput")
class SecureTextInput(CustomAction):
    def run(self, context: Context, argv: CustomAction.RunArg) -> CustomAction.RunResult:
        try:
            param = json.loads(argv.custom_action_param or "{}")
            field = param.get("field", "")
            if field not in FIELD_TO_KEY:
                logger.error(f"SecureTextInput: 非法 field={field!r}")
                return CustomAction.RunResult(success=False)

            data, device = _find_credentials()
            key = FIELD_TO_KEY[field]
            text = str(data.get(key, ""))
            if not _clean(text):
                logger.error(f"SecureTextInput: {key} 为空或含不安全字符")
                return CustomAction.RunResult(success=False)

            if not _send_via_adb(text, device):
                logger.error(f"SecureTextInput: adb 输入失败（{key}）")
                return CustomAction.RunResult(success=False)
            logger.info(f"SecureTextInput: {key} 已输入（长度 {len(text)}）")
            return CustomAction.RunResult(success=True)
        except Exception:
            logger.exception("SecureTextInput 失败")
            return CustomAction.RunResult(success=False)
