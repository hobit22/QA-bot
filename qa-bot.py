from langchain_community.agent_toolkits import PlayWrightBrowserToolkit
from langchain_community.tools.playwright.utils import (
    create_sync_playwright_browser,
    create_async_playwright_browser,  # A synchronous browser is available, though it isn't compatible with jupyter.\n",      },
)
from langchain_community.tools.playwright import ClickTool
import nest_asyncio
from typing import Literal
from playwright.async_api import Page, FloatRect
from typing import Any, Dict, List, Optional
from langchain.schema import AgentAction, AgentFinish
from uuid import UUID

from langchain.callbacks import manager

import pathlib
import typing
import asyncio
from langchain.callbacks.base import BaseCallbackHandler, ToolManagerMixin, AsyncCallbackHandler
from dotenv import load_dotenv
from langchain_community.tools.playwright.utils import (
    aget_current_page,
    get_current_page,
)
from langchain.callbacks.manager import CallbackManager
from langchain.callbacks.streaming_stdout import StreamingStdOutCallbackHandler
from langchain.agents import AgentType, initialize_agent


load_dotenv()

nest_asyncio.apply()
async_browser = create_async_playwright_browser(headless= False)
sync_browser = create_sync_playwright_browser(headless= False)
toolkit = PlayWrightBrowserToolkit.from_browser(sync_browser=sync_browser)
tools = toolkit.get_tools()

from langchain.chat_models import ChatOpenAI

llm = ChatOpenAI(
    temperature=0.3,
    # model="gpt-4",
    )

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

cHandler = TestHandler(async_browser= async_browser)
cManager = manager.AsyncCallbackManager(handlers=[cHandler])

agent_chain = initialize_agent(
    tools,
    llm,
    agent=AgentType.STRUCTURED_CHAT_ZERO_SHOT_REACT_DESCRIPTION,
    verbose=True,
    # callback_manager=cManager
)

async def test():
    result = await agent_chain.arun("""
                                    """)
    print(result)

# asyncio.run(test())

result = agent_chain.run("""
                                """)
print(result)

# asyncio.run(test())