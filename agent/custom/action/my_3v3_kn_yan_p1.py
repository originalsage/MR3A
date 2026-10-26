from maa.agent.agent_server import AgentServer
from maa.context import Context
from maa.custom_action import CustomAction

from custom.interruptible import interruptible_click, TaskStopRequested


@AgentServer.custom_action("my_3v3_kn_yan_p1")
class my_3v3_kn_yan_p1(CustomAction):
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
            click(1, 1, 800)
            click(1100, 620, 400)
            click(1100, 620, 600)
            click(200, 620, 250)
            click(1100, 620, 2500)

            click(1100, 620, 300)
            click(1100, 620, 300)
            click(200, 620, 300)

            click(1100, 620, 200)
            click(1100, 620, 200)
            click(200, 620, 500)
            click(200, 620, 100)

            # 尝试三段跳，二段跳会受伤但要确保稳定
            click(1100, 620, 300)
            click(1100, 620, 300)
            click(1100, 620, 700)
            click(200, 620, 250)

            click(1100, 620, 300)
            click(1100, 620, 400)
            click(200, 620, 450)

            # 主动二段跳踩刺防止卡墙导致时间错位
            click(1100, 620, 300)
            click(1100, 620, 300)
            click(200, 620, 200)

            click(1100, 620, 150)
            click(1100, 620, 150)
            click(200, 620, 200)

            click(1100, 620, 400)
            click(1100, 620, 500)
            click(200, 620, 1000)

            click(1100, 620, 300)
            click(1100, 620, 350)
            click(200, 620, 200)

            click(1100, 620, 350)
            click(1100, 620, 650)
            click(200, 620, 1400)
            click(200, 620, 1100)

            click(1100, 620, 100)
            click(1100, 620, 200)
            click(1100, 620, 1000)
            click(200, 620, 1550)

            click(1100, 620, 300)
            click(1100, 620, 400)
            click(1100, 620, 800)
            click(200, 620, 1600)

            click(1100, 620, 1200)
            click(200, 620, 1100)
            click(1100, 620, 600)
            click(200, 620, 800)
            click(1100, 620, 200)

            click(750, 600, 100)
            click(630, 600, 100)
            click(520, 600, 6500)
            click(370, 600, 6000)

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
