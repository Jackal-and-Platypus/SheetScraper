from scraper.commands.base import TestCommand


class WebWidthCommand(TestCommand):
    """
    處理瀏覽器視窗寬度調整的命令。
    這個命令不需要元素互動，而是直接操作瀏覽器視窗。
    """

    def _execute_command(self, step: dict) -> str:
        try:
            current_size = self.driver.get_window_size()
            # 保持原有的高度，只改變寬度
            self.driver.set_window_size(
                width=int(step["value"]), height=current_size["height"]
            )
            return "success"
        except Exception as e:
            print(f"Failed to set window width: {e}")
            return "failure"
