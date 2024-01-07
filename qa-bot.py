import nest_asyncio
from dotenv import load_dotenv

# langchain
from langchain.agents import AgentType, initialize_agent
from langchain.callbacks import manager
from langchain.chat_models import ChatOpenAI
from langchain_community.agent_toolkits import PlayWrightBrowserToolkit
from langchain_community.tools.playwright.utils import (
    create_sync_playwright_browser,
    create_async_playwright_browser,  # A synchronous browser is available, though it isn't compatible with jupyter.\n",      },
)

# my custom tools
from click_tool import ClickTool
from type_text_tool import TypeTextTool

# my custom handler
from test_handler import TestHandler

load_dotenv()

nest_asyncio.apply()
async_browser = create_async_playwright_browser(headless= False)
sync_browser = create_sync_playwright_browser(headless= False)
toolkit = PlayWrightBrowserToolkit.from_browser(sync_browser=sync_browser)
type_text_tool = TypeTextTool(sync_browser=sync_browser)
click_tool = ClickTool(sync_browser=sync_browser)
playwright_tools = toolkit.get_tools()
tools_by_name = {tool.name: tool for tool in playwright_tools}
navigate_browser = tools_by_name["navigate_browser"]


tools = [navigate_browser, type_text_tool, click_tool]
# tools = playwright_tools.append(type_text_tool)


llm = ChatOpenAI(
    temperature=0.3,
    # model="gpt-4",
    )

cHandler = TestHandler(async_browser= async_browser)
cManager = manager.AsyncCallbackManager(handlers=[cHandler])

agent_chain = initialize_agent(
    tools,
    llm,
    agent=AgentType.STRUCTURED_CHAT_ZERO_SHOT_REACT_DESCRIPTION,
    verbose=True,
    # callback_manager=cManager
)

result = agent_chain.run("""
                        1. go to https://m5-dev.matamath.net/vitruv.hs/login
                        2. type the text as hobeen.kim@vitruv.co.kr in username
                        3. type the text as 2023ejrmffhfl! in password
                        4. click "로그인"
                        5. click "마타와 연산학습"
                        end

                                """)
print(result)