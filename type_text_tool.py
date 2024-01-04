from __future__ import annotations
from playwright._impl._element_handle import ElementHandle

import json
from typing import TYPE_CHECKING, List, Optional, Sequence, Type

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

if TYPE_CHECKING:
    from playwright.async_api import Page as AsyncPage
    from playwright.sync_api import Page as SyncPage


class TypeTextToolInput(BaseModel):
    """Input for TypeTextTool."""
    element: Optional["ElementHandle"] = Field(
            None,
            description="ElementHandle to type into. If provided, selector is ignored."
        )
    selector: str = Field(
        ...,
        description="CSS selector, such as 'input', 'textarea', '#id', '.classname'"
    )
    text: str = Field(
        ...,
        description="Text to be typed into the selected element"
    )
    
def _get_element_sync(page: SyncPage, selector: str):
    return page.query_selector(selector)

# 비동기 방식의 getElement 구현
async def _get_element_async(page: AsyncPage, selector: str):
    return await page.query_selector(selector)

async def _atype_text(page: AsyncPage, selector: str, text: str) -> None:
    """Type text into an element matching the given CSS selector."""
    await page.type(selector, text)


def _type_text(page: SyncPage, selector: str, text: str) -> None:
    """Type text into an element matching the given CSS selector."""
    page.type(selector, text).result()


class TypeTextTool(BaseBrowserTool):
    """Tool for typing text into elements in the current web page matching a CSS selector."""

    name: str = "type_text"
    description: str = (
        "Type text into an element in the current web page matching the given CSS selector"
    )
    args_schema: Type[BaseModel] = TypeTextToolInput
    def _run(
            self,
            selector: str,
            text: str,
            run_manager: Optional[CallbackManagerForToolRun] = None,
        ) -> str:
            if self.sync_browser is None:
                raise ValueError(f"Synchronous browser not provided to {self.name}")
            page = get_current_page(self.sync_browser)
            element = _get_element_sync(page, selector)
            if element is None:
                raise ValueError(f"Element with selector '{selector}' not found")
            _type_text(page, selector, text)
            return f"Typed '{text}' into elements with selector '{selector}'"

    async def _arun(
        self,
        selector: str,
        text: str,
        run_manager: Optional[AsyncCallbackManagerForToolRun] = None,
    ) -> str:
        if self.async_browser is None:
            raise ValueError(f"Asynchronous browser not provided to {this.name}")
        page = await aget_current_page(self.async_browser)
        element = await _get_element_async(page, selector)
        if element is None:
            raise ValueError(f"Element with selector '{selector}' not found")
        await _atype_text(page, selector, text)
        return f"Typed '{text}' into elements with selector '{selector}'"