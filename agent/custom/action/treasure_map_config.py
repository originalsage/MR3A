import json

from maa.agent.agent_server import AgentServer
from maa.custom_action import CustomAction
from maa.context import Context

from utils import logger


@AgentServer.custom_action("ApplyTreasureMapConfig")
class ApplyTreasureMapConfig(CustomAction):
    """
    读取来源节点 A 的 attach，将解析后的 expected 写入目标节点 B。

    参数 (custom_action_param, JSON 字符串):
        source  (str): 读取 attach 的来源节点名，默认 "刷别人的藏宝图"
        targets (list[str]): 写入 expected 的目标节点名列表,
                             默认 ["藏宝图上层识别到目标藏宝图", "藏宝图下层识别到目标藏宝图"]
        space_between_quality_attr (bool): 为 True 时，expected 同时包含带空格与不带空格两种形式；
                             日志始终打印不带空格形式；默认 False（仅不带空格）

    attach key 格式: "{品质}{属性}"，如 "神品云之国"。
    多个 checkbox 勾选会通过 dict merge 合并到同一个 attach 中。
    """

    QUALITIES = ["神品", "绝品", "珍品", "凡品"]
    ATTRIBUTES = ["云之国", "海之国", "神炎国", "雷王山"]

    DEFAULT_SOURCE = "刷别人的藏宝图"
    DEFAULT_TARGETS = [
        "藏宝图上层识别到目标藏宝图",
        "藏宝图下层识别到目标藏宝图",
    ]

    def run(
        self,
        context: Context,
        argv: CustomAction.RunArg,
    ) -> CustomAction.RunResult:
        # ── 解析参数 ──────────────────────────────────────────
        source = self.DEFAULT_SOURCE
        targets = self.DEFAULT_TARGETS
        space_between_quality_attr = False

        if argv.custom_action_param:
            if isinstance(argv.custom_action_param, dict):
                param = argv.custom_action_param
            else:
                try:
                    param = json.loads(argv.custom_action_param)
                except (json.JSONDecodeError, TypeError) as e:
                    logger.error(f"参数解析失败: {e}")
                    return CustomAction.RunResult(success=False)
            if param:
                source = param.get("source", self.DEFAULT_SOURCE)
                targets = param.get("targets", self.DEFAULT_TARGETS)
                space_between_quality_attr = param.get(
                    "space_between_quality_attr", False
                )

        # ── 读取来源节点 ─────────────────────────────────────
        config_node = context.get_node_data(source)
        attach = config_node.get("attach", {}) if config_node else {}

        if not attach:
            logger.info(f"未选择藏宝图，任务结束 ({source})")
            return CustomAction.RunResult(success=False)

        # ── 从 attach key 解析品质+属性组合（value 为 false 的跳过） ──
        parsed = []
        for key, value in attach.items():
            if not value:
                continue
            matched_quality = None
            matched_attr = None
            for q in self.QUALITIES:
                if key.startswith(q):
                    matched_quality = q
                    matched_attr = key[len(q) :]
                    break
            if matched_quality and matched_attr in self.ATTRIBUTES:
                parsed.append((matched_quality, matched_attr))
            else:
                logger.warning(f"无法解析 attach key {key!r}，已跳过 ({source})")

        if not parsed:
            logger.error(f"attach 中无有效的品质+属性组合 ({source})")
            return CustomAction.RunResult(success=False)

        # ── 按品质→属性排序 ──────────────────────────────────
        parsed.sort(
            key=lambda x: (
                self.QUALITIES.index(x[0]),
                self.ATTRIBUTES.index(x[1]),
            )
        )
        plain_expected = [f"{q}{a}" for q, a in parsed]
        spaced_expected = [f"{q} {a}" for q, a in parsed]
        map_expected = (
            plain_expected + spaced_expected
            if space_between_quality_attr
            else plain_expected
        )

        # ── 写入各目标节点 expected ────────────────────────────
        override = {}
        for target in targets:
            override[target] = {"recognition": {"param": {"expected": map_expected}}}

        if not context.override_pipeline(override):
            logger.error(f"override_pipeline 失败 ({source})")
            return CustomAction.RunResult(success=False)

        logger.info(f"{source}: {len(parsed)} 个组合 {plain_expected}")
        return CustomAction.RunResult(success=True)


@AgentServer.custom_action("RemoveQualityFromAttach")
class RemoveQualityFromAttach(CustomAction):
    """
    将指定品质在目标节点 attach 中的条目设为 false（次数为0）。

    参数 (custom_action_param, JSON 字符串或 dict):
        node_name         (str):  目标节点名
        quality           (str):  要排除的品质，如 "凡品"、"珍品"、"绝品"
        check_all_cleared (bool): 写入后检查绝品/珍品/凡品是否全部清完，是则返回 success=False
    """

    QUALITIES = ["神品", "绝品", "珍品", "凡品"]
    DAILY_QUALITIES = ["绝品", "珍品", "凡品"]

    def run(
        self,
        context: Context,
        argv: CustomAction.RunArg,
    ) -> CustomAction.RunResult:
        if not argv.custom_action_param:
            logger.error("RemoveQualityFromAttach: 缺少参数")
            return CustomAction.RunResult(success=False)

        if isinstance(argv.custom_action_param, dict):
            param = argv.custom_action_param
        else:
            try:
                param = json.loads(argv.custom_action_param)
            except (json.JSONDecodeError, TypeError) as e:
                logger.error(f"RemoveQualityFromAttach: 参数解析失败 {e}")
                return CustomAction.RunResult(success=False)

        node_name = param.get("node_name")
        quality = param.get("quality")

        if not node_name or quality not in self.QUALITIES:
            logger.error(
                f"RemoveQualityFromAttach: 参数无效 node_name={node_name} quality={quality}"
            )
            return CustomAction.RunResult(success=False)

        config_node = context.get_node_data(node_name)
        attach = dict(config_node.get("attach", {})) if config_node else {}

        if not attach:
            logger.debug(f"RemoveQualityFromAttach: {node_name}.attach 为空，无需操作")
            return CustomAction.RunResult(success=True)

        # 将该品质的所有条目设为 false（dict merge 会覆盖同名 key）
        override_attach = {}
        for k in attach:
            if k.startswith(quality):
                override_attach[k] = False
        if override_attach:
            override = {node_name: {"attach": override_attach}}
            if not context.override_pipeline(override):
                logger.error(f"RemoveQualityFromAttach: override_pipeline 失败")
                return CustomAction.RunResult(success=False)
            logger.debug(
                f"RemoveQualityFromAttach: {node_name} 已排除 {quality} ({len(override_attach)} 个条目)"
            )

        # ── 检查每日次数是否全部清完 ──────────────────────────
        check_all_cleared = param.get("check_all_cleared", False)
        if check_all_cleared:
            remaining_daily = False
            for k, v in attach.items():
                if k in override_attach:
                    v = override_attach[k]
                if v and any(k.startswith(q) for q in self.DAILY_QUALITIES):
                    remaining_daily = True
                    break
            if not remaining_daily:
                logger.info("每日次数已全部清完，任务结束")
                return CustomAction.RunResult(success=False)

        return CustomAction.RunResult(success=True)
