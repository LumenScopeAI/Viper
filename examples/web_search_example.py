"""
网络搜索示例 - 演示如何使用LLMAgent和WebProtocol执行网络搜索任务
"""

import os
import sys
import json
import logging
from typing import Dict, Any

# 添加项目根目录到路径
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from orchestration.llm_agent import LLMAgent
from orchestration.agents_manager import AgentsManager
from protocols.web_protocol import WebProtocol


# 配置日志
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)

logger = logging.getLogger("WebSearchExample")


def setup_agent() -> LLMAgent:
    """
    设置LLM智能体
    
    Returns:
        配置好的LLM智能体
    """
    # 获取OpenAI API密钥
    api_key = os.environ.get("OPENAI_API_KEY")
    if not api_key:
        raise ValueError("请设置OPENAI_API_KEY环境变量")
    
    # 创建LLM智能体
    agent = LLMAgent(
        name="搜索助手",
        description="我是一个网络搜索助手，可以帮助你搜索和提取网页内容。",
        model="gpt-3.5-turbo",
        api_key=api_key
    )
    
    # 创建Web协议
    web_protocol = WebProtocol()
    
    # 注册工具到智能体
    agent.register_tool(
        name="search_web",
        func=lambda url: web_protocol.execute_tool("fetch_and_extract", url=url),
        description="搜索一个网页并提取内容，参数：url (网页URL)"
    )
    
    agent.register_tool(
        name="extract_info",
        func=lambda html_content, query: web_protocol.execute_tool("search_content", html_content=html_content, query=query),
        description="从HTML内容中搜索特定信息，参数：html_content (HTML内容), query (搜索关键词)"
    )
    
    return agent


def search_website(agent: LLMAgent, url: str, query: str) -> Dict[str, Any]:
    """
    使用智能体搜索网站
    
    Args:
        agent: LLM智能体
        url: 要搜索的网站URL
        query: 搜索查询
        
    Returns:
        搜索结果
    """
    # 构建任务描述
    task = f"""
请帮我搜索以下网站并回答问题：

网站: {url}
问题: {query}

请按照以下步骤操作:
1. 使用search_web工具获取网页内容
2. 分析内容，找出与问题相关的信息
3. 如果需要，使用extract_info工具搜索特定内容
4. 用简洁明了的语言总结答案
"""
    
    # 执行任务
    logger.info(f"开始搜索网站: {url}")
    logger.info(f"搜索问题: {query}")
    
    result = agent.run(task)
    
    logger.info("搜索完成")
    return result


def print_result(result: Dict[str, Any]) -> None:
    """
    打印搜索结果
    
    Args:
        result: 搜索结果
    """
    print("\n" + "="*50)
    print("搜索结果:")
    print("="*50)
    
    if isinstance(result, dict):
        if "result" in result:
            print(result["result"])
        if "summary" in result:
            print("\n摘要:")
            print(result["summary"])
    else:
        print(result)
    
    print("="*50 + "\n")


def main():
    """主函数"""
    try:
        # 设置智能体
        agent = setup_agent()
        
        # 用户输入
        print("网络搜索示例")
        print("="*50)
        
        url = input("请输入要搜索的网站URL: ") or "https://www.python.org"
        query = input("请输入要搜索的问题: ") or "Python 3.11有什么新特性？"
        
        # 执行搜索
        result = search_website(agent, url, query)
        
        # 打印结果
        print_result(result)
    
    except Exception as e:
        logger.error(f"发生错误: {e}")
        print(f"错误: {e}")


if __name__ == "__main__":
    main() 