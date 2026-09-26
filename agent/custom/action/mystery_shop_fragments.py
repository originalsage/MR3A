import re

from maa.agent.agent_server import AgentServer
from maa.custom_action import CustomAction
from maa.context import Context

from utils import logger


CONFIG_NODE = "勾玉购买忍者碎片配置"
# 游戏里只有第 8 个商品位会刷勾玉碎片（0-based：商品7）。
FRAGMENT_SLOT = 7
FRAGMENT_NODE = f"神秘商店商品{FRAGMENT_SLOT}是配置碎片"


def fragment_pattern(name: str) -> str:
    return re.escape(name) + r".*碎片"


def selected_fragment_names(attach: dict) -> list[str]:
    """GUI/checkbox 勾选后写入 attach；Agent 只消费已选项。"""
    return [str(key) for key, value in attach.items() if value]


@AgentServer.custom_action("ApplyMysteryShopFragmentConfig")
class ApplyMysteryShopFragmentConfig(CustomAction):
    """
    读取勾玉购买忍者碎片配置的 attach，把已勾选全名写入第 8 商品位的碎片识别。

    待选项只在 日常任务.json 的 checkbox cases 里维护；框架把选中项合并进 attach。
    Agent 不持有完整名单，只根据 attach 里为 true 的 key 购买。
    没有勾选时该商品位保持关闭，商店继续只买忍币商品。
    """

    def run(
        self,
        context: Context,
        argv: CustomAction.RunArg,
    ) -> CustomAction.RunResult:
        del argv
        config_node = context.get_node_data(CONFIG_NODE)
        attach = config_node.get("attach", {}) if config_node else {}
        selected = selected_fragment_names(attach if isinstance(attach, dict) else {})

        if not selected:
            logger.info("未勾选勾玉忍者碎片")
            return CustomAction.RunResult(success=True)

        expected = [fragment_pattern(name) for name in selected]
        override = {
            FRAGMENT_NODE: {
                "enabled": True,
                "recognition": {"param": {"expected": expected}},
            }
        }
        if not context.override_pipeline(override):
            logger.error("勾玉碎片 override_pipeline 失败")
            return CustomAction.RunResult(success=False)

        logger.info(f"勾玉碎片: {selected}")
        return CustomAction.RunResult(success=True)
