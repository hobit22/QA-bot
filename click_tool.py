from __future__ import annotations

from typing import Optional, Type

from langchain_core.callbacks import (
    AsyncCallbackManagerForToolRun,
    CallbackManagerForToolRun,
)
from langchain_core.pydantic_v1 import BaseModel, Field

from langchain_community.tools.playwright.base import BaseBrowserTool
from langchain_community.tools.playwright.utils import (
    aget_current_page,
    get_current_page,
)


class ClickToolInput(BaseModel):
    """Input for ClickTool."""

    text: str = Field(
        ..., 
        description="The text that the element you are looking for has"
)


class ClickTool(BaseBrowserTool):
    """Tool for clicking on an element with the given text."""

    name: str = "click_element"
    description: str = "Click on an element with the given text"
    args_schema: Type[BaseModel] = ClickToolInput

    visible_only: bool = True
    """Whether to consider only visible elements."""
    playwright_strict: bool = True
    """Whether to employ Playwright's strict mode when clicking on elements."""
    playwright_timeout: float = 1_000
    """Timeout (in ms) for Playwright to wait for element to be ready."""

    def _selector_effective(self, selector: str) -> str:
        if not self.visible_only:
            return selector
        return f"{selector} >> visible=true"

    def _run(
        self,
        text: str,
        run_manager: Optional[CallbackManagerForToolRun] = None,
    ) -> str:
        """Use the tool."""
        if self.sync_browser is None:
            raise ValueError(f"Synchronous browser not provided to {self.name}")
        page = get_current_page(self.sync_browser)
        # Navigate to the desired webpage before using this tool
        selector_effective = self._selector_effective(selector=text)
        # selector_effective = f"text={selector}"
        from playwright.sync_api import TimeoutError as PlaywrightTimeoutError
        element = page.get_by_text(text)
        print(element)

        try:
            element.click(
                # strict=self.playwright_strict,
                timeout=self.playwright_timeout
            )
        except PlaywrightTimeoutError:
            return f"Unable to click on element '{text}'"
        return f"Clicked element '{text}'"

    async def _arun(
        self,
        selector: str,
        run_manager: Optional[AsyncCallbackManagerForToolRun] = None,
    ) -> str:
        """Use the tool."""
        if self.async_browser is None:
            raise ValueError(f"Asynchronous browser not provided to {self.name}")
        page = await aget_current_page(self.async_browser)
        # Navigate to the desired webpage before using this tool
        selector_effective = self._selector_effective(selector=selector)
        from playwright.async_api import TimeoutError as PlaywrightTimeoutError

        try:
            await page.click(
                selector_effective,
                strict=self.playwright_strict,
                timeout=self.playwright_timeout,
            )
        except PlaywrightTimeoutError:
            return f"Unable to click on element '{selector}'"
        return f"Clicked element '{selector}'"
