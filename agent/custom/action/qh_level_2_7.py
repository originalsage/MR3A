from maa.agent.agent_server import AgentServer
from maa.context import Context
from maa.custom_action import CustomAction

from custom.interruptible import interruptible_click, TaskStopRequested


@AgentServer.custom_action("qh_level_2_7")
class qh_level_2_7(CustomAction):
    def run(
        self,
        context: Context,
        argv: CustomAction.RunArg,
    ) -> CustomAction.RunResult:
        """
        3v3 点击动作
        直接在代码中添加点击逻辑，格式：
        # 点击[x,y]delay t
        其中 x,y 是点击坐标，t 是延迟时间（毫秒）
        """
        try:

            def click(x, y, delay_ms=0):
                if not interruptible_click(context, x, y, delay_ms):
                    raise TaskStopRequested

            # ===================
            # 在这里添加你的点击序列
            # ===================
            # click(200, 620, t) 为下翻
            # click(1100, 620, t) 为跳跃
            click(1100, 620, 1200)
            click(1100, 620, 2000)

            click(1100, 620, 200)
            click(1100, 620, 1400)

            click(1100, 620, 200)
            click(1100, 620, 2000)

            click(1100, 620, 200)
            click(1100, 620, 1500)

            click(1100, 620, 200)
            click(1100, 620, 300)
            click(200, 620, 400)

            click(1100, 620, 200)
            click(1100, 620, 19200)
            click(1100, 620, 5600)
            click(1100, 620, 200)
            click(1100, 620, 1700)
            click(1100, 620, 2000)

            click(1100, 620, 2200)
            click(1100, 620, 1700)

            click(1100, 620, 200)
            click(1100, 620, 1000)

            click(1100, 620, 200)
            click(1100, 620, 1300)

            click(1100, 620, 4000)

            click(1100, 620, 1000)

            click(1100, 620, 2000)

            # ===================
            # 结束点击序列
            # ===================

            return CustomAction.RunResult(success=True)
        except TaskStopRequested:
            return CustomAction.RunResult(success=False)
        except Exception as e:
            import logging

            logging.error(f"执行3v3点击时出错: {e}")
            print(f"执行3v3点击时出错: {e}")
            return CustomAction.RunResult(success=False)
