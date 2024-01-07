import pathlib
import typing
from typing import Any, Dict, List, Optional
from uuid import UUID
from playwright.async_api import Page, FloatRect

# langchain
from langchain.callbacks.base import BaseCallbackHandler, ToolManagerMixin, AsyncCallbackHandler
from langchain_community.tools.playwright.utils import (
    aget_current_page,
    get_current_page,
)
from langchain.schema import AgentAction, AgentFinish

class TestHandler(AsyncCallbackHandler):
    def __init__(self, async_browser, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.async_browser = async_browser

    async def save_screenshot(
        self,
        page: Page,
        file_path: typing.Optional[typing.Union[str, pathlib.Path]] = "screenshot.png",
        full_page: typing.Optional[bool] = True,
        # ... 기타 매개변수들 ...
    ) -> None:
        screenshot_bytes = await page.screenshot(path="./screenshot.png", full_page=full_page )
        print("save_screenshot 실행~")
        print("path : {file_path}")
        with open(file_path, 'wb') as file:
            print("open?")
            file.write(screenshot_bytes)

    async def on_tool_end(self, output: str, observation_prefix: Optional[str] = None, llm_prefix: Optional[str] = None, **kwargs: Any) -> Any:
        page = await aget_current_page(self.async_browser)  # 현재 페이지 객체 가져오기
        await self.save_screenshot(page=page)  # 스크린샷 저장
        print("on_tool_end")

    def on_agent_action(self, action: AgentAction, **kwargs: Any) -> Any:
        """Run on agent action."""
        print("on_agent_action")

    async def on_agent_finish(
        self,
        finish: AgentFinish,
        *,
        run_id: UUID,
        parent_run_id: Optional[UUID] = None,
        **kwargs: Any,
    ) -> Any:
        """Run on agent end."""
        page = await aget_current_page(self.async_browser)  # 현재 페이지 객체 가져오기
        await self.save_screenshot(page=page)  # 스크린샷 저장
        print("on_agent_finish")