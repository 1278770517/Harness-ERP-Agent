import asyncio
from pathlib import Path
import yaml
from deepagents import create_deep_agent
from langchain_openai import ChatOpenAI

from src.mcp_tool.mcp_tool_config import mcp_client
from src.sandbox_demo.my_tools import web_search
from src.sandbox_demo.opensandbox_opt import get_or_create_sandbox, config, sync_skills_to_sandbox
from src.sandbox_demo.custom_opensandbox import OpenSandboxBackend
from src.util import QWEN_URl, QWEN_API

llm=ChatOpenAI(
    model='qwen-max',
    base_url=QWEN_URl,
    api_key=QWEN_API
)

EXAMPLE_DIR = Path(__file__).parent.parent.parent
print(f'当前代码执行的工作目录为：{EXAMPLE_DIR}')
chart_tools=mcp_client.get_tools(server_name="fenxi")
available_tools = {
        # "xsct": xsct_tools,
        "fenxi": chart_tools,
        "web_search": [web_search],
    }
async def load_subagents(config_path: str):
    with open(config_path, "r") as f:
        config=yaml.safe_load(f)
    subagents=[]
    for name,spec in config.items():
        subagent={
            "name": name,
            "description": spec["description"],
            "system_prompt": spec["system_prompt"],
        }
        if "model" in spec:
            subagent["model"] = spec["model"]
        if "tool" in spec:
            tools = [available_tools[t] for t in spec["tools"]]
            print(tools)
            subagent["tools"] = tools[0]
        subagents.append(subagent)
    return subagents
async def crete():
    subagents=await load_subagents(EXAMPLE_DIR / 'subagents.yaml')
    sandbox=get_or_create_sandbox(config)
    backend=OpenSandboxBackend(sandbox=sandbox)
    local_skills_path = str(EXAMPLE_DIR / "src/skill")

    # 沙箱中的技能目录
    sandbox_skills_path = "/workspace/skills"

    # 智能同步技能到沙箱
    uploaded_count = sync_skills_to_sandbox(backend, local_skills_path, sandbox_skills_path)
    with open(str(EXAMPLE_DIR / "AGENTS.md"), 'r', encoding='utf-8') as f:
        print(str(EXAMPLE_DIR / "AGENTS.md"))
        content = f.read()

    result = backend.upload_files([('/AGENTS.md', content.encode("utf-8"))])

    if uploaded_count > 0:
        print(f"✅ 成功上传了 {uploaded_count} 个新技能到沙箱")
    else:
        print("✅ 所有技能已存在于沙箱中，无需上传")

    return create_deep_agent(
        model=llm,
        skills=[sandbox_skills_path],
        memory=['/AGENTS.md'],
        tools=[web_search],
        backend=backend,
        subagents=subagents,
    )
agent=asyncio.run( crete())










