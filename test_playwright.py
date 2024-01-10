
from langchain_community.tools.playwright.utils import (
    create_sync_playwright_browser,
    create_async_playwright_browser,  # A synchronous browser is available, though it isn't compatible with jupyter.\n",      },
)
import nest_asyncio

import typing
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
from playwright._impl._element_handle import ElementHandle
nest_asyncio.apply()

def _get_element(
    page: SyncPage, selector: str, attributes: Sequence[str]
) -> typing.Optional["ElementHandle"]:
    """Get elements matching the given text."""
    elements = page.query_selector_all(selector)
    results = []
    for element in elements:
        result = {}
        for attribute in attributes:
            if attribute == "innerText":
                val: Optional[str] = element.inner_text()
            else:
                val = element.get_attribute(attribute)
            if val is not None and val.strip() != "":
                result[attribute] = val
        if result:
            results.append(result)
    return elements[0]

sync_browser = create_sync_playwright_browser(headless= False)

context = sync_browser.new_context()
page = context.new_page()

elements = _get_element(page, )