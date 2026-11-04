from langchain_core.tools import tool
from zai import ZhipuAiClient


client = ZhipuAiClient(api_key='09a9e7452f314f8aa2f0c3a693a57486.9MVp3QWHm5TvgcVr')


@tool('web_search', parse_docstring=True)
def web_search(query: str) -> str:
    """
    使用搜狗的API进行Web搜索

    Args:
        query: 需要搜索的内容或者关键字。

    Returns:
        返回搜索之后的结果
    """
    try:
        response = client.web_search.web_search(
            search_engine="search_pro",
            search_query=query,
            count=3,  # 返回结果的条数，范围1-50，默认10
            search_recency_filter="noLimit",  # 搜索指定日期范围内的内容
        )
        if response.search_result:
            return "\n\n".join([d.content for d in response.search_result])
        return '没有搜索到任何内容！'
    except Exception as e:
        print(e)
        return f"搜索失败: {e}"
