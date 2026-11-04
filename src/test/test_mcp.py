import asyncio
from fastmcp.client import Client
from langchain_mcp_adapters.client import MultiServerMCPClient

from src.mcp_server.server_main import mcp
c = Client("http://localhost:8000/mcp")

async def mcp_client():
    """创建内存模式客户端固件"""
    async with Client(mcp) as client:
        # result = await client.call_tool("supplier_query", {
        #     "params": {
        #         "current": 1,
        #         "size": 10,
        #         "name": "博世",
        #         # "status": 1,
        #         # "creditRating": "A"
        #     }
        # })
        # result = await client.call_tool("order_update", {
        #     "order_id": 1,
        #     "actual_delivery_date": "2024-12-25",
        #      "order_number": 'PO2026000001',
        #     "created_by": 11,
        #     "remark": "卸腿、头、甲、抢、胸挂、背包、❀来"
        #
        # })
        # result = await client.call_tool("create_order", {
        #     "order_id": 1,
        #     "actual_delivery_date": "2024-12-25",
        #     "order_number": 'PO2026000001',
        #     "created_by": 11,
        #     "remark": "供应商变更，交货日期延后"
        #
        # })
        # result = await client.call_tool("order_search_details", {
        #     "part_name":"发动机缸体",
        #     "start_date": "2025-01-18",
        #     "end_date": ""
        #
        # })
        result = await client.call_tool("supplier_query", {
            'name':'KYB（中国）投资有限公司'
            # "supplier_id": 26

        })

        print(result)


async def agent_client():
    mcp_server_config = {
        "url": "http://127.0.0.1:8000/mcp",
        "transport": "streamable_http",
    }
    # 创建一个mcp的客户端
    mcp_client = MultiServerMCPClient({
        # "xsct": xsct_mcp_server_config,
        "api": mcp_server_config,
    })
    all_tools = await mcp_client.get_tools(server_name="api")
    print(all_tools)
    # tools = [t for t in all_tools if t.name.startswith(f"{group_name}_")]
    tools = [t for t in all_tools if t.name.startswith(f"part_")]
    print(tools)

if __name__ == '__main__':
    asyncio.run(mcp_client())
    # asyncio.run(agent_client())

# @pytest.mark.asyncio
# async def test_list_all_tools(mcp_client):
#     """验证所有工具是否已正确注册"""
#     tools = await mcp_client.list_tools()
#     tool_names = [tool.name for tool in tools]
#
#     # 验证三个分组共6个工具已注册
#     expected_tools = [
#         "user_get_user", "user_list_users",
#         "order_create", "order_list",
#         "product_get", "product_search"
#     ]
#     assert len(tools) == 6
#     for expected in expected_tools:
#         assert expected in tool_names
#
#
# @pytest.mark.asyncio
# async def test_user_get_tool(mcp_client):
#     """验证 user_get_user 工具"""
#     result = await mcp_client.call_tool(
#         "user_get_user",
#         arguments={"user_id": 123}
#     )
#     content = json.loads(result[0].text)
#
#     # 注意：实际结果取决于 Java 后端 API 返回的内容
#     assert "error" not in content
#     assert isinstance(content, dict)
#
#
# @pytest.mark.asyncio
# async def test_order_create_with_pydantic(mcp_client):
#     """验证 order_create 工具 - 使用 Pydantic 模型"""
#     result = await mcp_client.call_tool(
#         "order_create",
#         arguments={"input_data": {
#             "product_id": 456,
#             "quantity": 2,
#             "user_id": 123
#         }}
#     )
#     content = json.loads(result[0].text)
#     assert isinstance(content, dict)