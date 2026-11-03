#!/usr/bin/env python3
"""从 BWiki 刷新勾玉碎片 GUI 待选项（日常任务.json → 勾玉购买忍者碎片.cases）。

Agent 只买 attach 已选项，不持有名单。wiki 滞后时直接改上述 cases。
手动 CI：GitHub Actions「Sync fragment roster」，或本地跑本脚本。
"""

from __future__ import annotations

import argparse
import json
import sys
import time
import urllib.parse
import urllib.request
from pathlib import Path

ROOT = Path(__file__).resolve().parents[2]
TASKS_PATH = ROOT / "assets" / "resource" / "tasks" / "日常任务.json"
OPTION_KEY = "勾玉购买忍者碎片"
CONFIG_NODE = "勾玉购买忍者碎片配置"
CATEGORIES = ("作战忍者", "作战角色")
USER_AGENT = "MR3A/1.0 (fragment roster updater; +https://github.com/originalsage/MR3A)"
API = "https://wiki.biligame.com/nmd3/api.php"
RETRIES = 3


def _request_json(params: dict) -> dict:
    url = API + "?" + urllib.parse.urlencode(params)
    last_error: Exception | None = None
    for attempt in range(1, RETRIES + 1):
        t0 = time.perf_counter()
        try:
            req = urllib.request.Request(url, headers={"User-Agent": USER_AGENT})
            with urllib.request.urlopen(req, timeout=20) as resp:
                body = resp.read()
                ms = round((time.perf_counter() - t0) * 1000)
                print(f"HTTP {resp.status} ({ms}ms, {len(body)} bytes) attempt={attempt}")
                return json.loads(body)
        except Exception as e:
            last_error = e
            print(f"WARN: fetch failed attempt={attempt}: {e}", file=sys.stderr)
            if attempt < RETRIES:
                time.sleep(attempt * 2)
    raise RuntimeError(f"BWiki fetch failed after {RETRIES} attempts: {last_error}")


def fetch_category_titles(category: str) -> list[str]:
    titles: list[str] = []
    cont: str | None = None
    while True:
        params = {
            "action": "query",
            "list": "categorymembers",
            "cmtitle": f"Category:{category}",
            "cmlimit": "500",
            "cmnamespace": "0",
            "format": "json",
        }
        if cont:
            params["cmcontinue"] = cont
        data = _request_json(params)
        members = data.get("query", {}).get("categorymembers", [])
        titles.extend(m["title"] for m in members if "title" in m)
        cont = data.get("continue", {}).get("cmcontinue")
        if not cont:
            break
    return titles


def fetch_roster() -> list[str]:
    seen: set[str] = set()
    names: list[str] = []
    for category in CATEGORIES:
        for title in fetch_category_titles(category):
            if "·" not in title or title in seen:
                continue
            seen.add(title)
            names.append(title)
    if not names:
        raise RuntimeError("BWiki returned empty combat roster")
    return names


def load_task_case_names(tasks_path: Path) -> list[str]:
    tasks = json.loads(tasks_path.read_text(encoding="utf-8"))
    option = tasks.get("option", {}).get(OPTION_KEY)
    if not isinstance(option, dict):
        raise KeyError(f"missing option {OPTION_KEY!r}")
    cases = option.get("cases") or []
    return [str(case["name"]) for case in cases if isinstance(case, dict) and "name" in case]


def merge_order(old: list[str], fetched: list[str]) -> list[str]:
    fetched_set = set(fetched)
    kept = [name for name in old if name in fetched_set]
    kept_set = set(kept)
    added = [name for name in fetched if name not in kept_set]
    return kept + added


def fragment_checkbox_cases(names: list[str]) -> list[dict]:
    return [
        {
            "name": name,
            "pipeline_override": {
                CONFIG_NODE: {
                    "attach": {
                        name: True,
                    }
                }
            },
        }
        for name in names
    ]


def sync_tasks_cases(tasks_path: Path, names: list[str]) -> bool:
    tasks = json.loads(tasks_path.read_text(encoding="utf-8"))
    option = tasks.get("option", {}).get(OPTION_KEY)
    if not isinstance(option, dict):
        raise KeyError(f"missing option {OPTION_KEY!r} in {tasks_path}")
    new_cases = fragment_checkbox_cases(names)
    if option.get("cases") == new_cases:
        return False
    option["cases"] = new_cases
    tasks_path.write_text(
        json.dumps(tasks, ensure_ascii=False, indent=4) + "\n",
        encoding="utf-8",
    )
    return True


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser(
        description=(
            "从 BWiki 刷新勾玉碎片待选项。"
            "唯一维护处: assets/resource/tasks/日常任务.json → 勾玉购买忍者碎片.cases"
        )
    )
    parser.parse_args(argv)

    try:
        fetched = fetch_roster()
    except Exception as e:
        print(f"ERROR: {e}", file=sys.stderr)
        return 1

    try:
        old = load_task_case_names(TASKS_PATH)
    except Exception as e:
        print(f"ERROR: {e}", file=sys.stderr)
        return 1

    names = merge_order(old, fetched)
    print(f"Options: {len(names)} names ({len(names) - len(old):+d} vs tasks)")
    print(f"Maintained in: {TASKS_PATH.relative_to(ROOT)} → option[{OPTION_KEY!r}].cases")

    try:
        changed = sync_tasks_cases(TASKS_PATH, names)
    except Exception as e:
        print(f"ERROR: sync tasks failed: {e}", file=sys.stderr)
        return 1

    if changed:
        print(f"Updated {TASKS_PATH.relative_to(ROOT)}")
    else:
        print("No change")
    return 0


if __name__ == "__main__":
    sys.exit(main())
