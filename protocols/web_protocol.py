"""
网络协议 - 提供网络访问和搜索功能的MCP协议实现
"""

import json
from typing import Dict, List, Optional, Union, Any

from protocols.base_protocol import BaseProtocol
from tools.web_scraper import WebScraper


class WebProtocol(BaseProtocol):
    """
    网络协议类，遵循MCP协议规范，封装WebScraper工具
    
    提供以下功能:
    1. 获取网页内容
    2. 提取网页内容（标题、文本、链接等）
    3. 搜索网页内容
    """
    
    def __init__(self):
        """初始化WebProtocol"""
        super().__init__(
            name="WebProtocol",
            version="1.0.0",
            description="提供网络访问和搜索功能的MCP协议"
        )
        
        # 初始化WebScraper工具
        self.scraper = WebScraper()
        
        # 注册工具
        self._register_tools()
    
    def _register_tools(self):
        """注册协议提供的工具"""
        
        # 获取网页内容工具
        self.register_tool(
            name="get_page",
            func=self._get_page,
            description="获取网页内容",
            parameters={
                "type": "object",
                "properties": {
                    "url": {"type": "string", "description": "网页URL"},
                    "params": {"type": "object", "description": "请求参数", "optional": True}
                },
                "required": ["url"]
            },
            returns={
                "type": "object",
                "properties": {
                    "content": {"type": "string", "description": "网页内容"},
                    "url": {"type": "string", "description": "请求的URL"}
                }
            }
        )
        
        # 提取网页标题工具
        self.register_tool(
            name="extract_title",
            func=self._extract_title,
            description="从HTML内容中提取标题",
            parameters={
                "type": "object",
                "properties": {
                    "html_content": {"type": "string", "description": "HTML内容"},
                },
                "required": ["html_content"]
            },
            returns={
                "type": "object",
                "properties": {
                    "title": {"type": "string", "description": "网页标题"}
                }
            }
        )
        
        # 提取网页文本工具
        self.register_tool(
            name="extract_text",
            func=self._extract_text,
            description="从HTML内容中提取纯文本",
            parameters={
                "type": "object",
                "properties": {
                    "html_content": {"type": "string", "description": "HTML内容"},
                },
                "required": ["html_content"]
            },
            returns={
                "type": "object",
                "properties": {
                    "text": {"type": "string", "description": "提取的文本内容"}
                }
            }
        )
        
        # 提取网页链接工具
        self.register_tool(
            name="extract_links",
            func=self._extract_links,
            description="从HTML内容中提取所有链接",
            parameters={
                "type": "object",
                "properties": {
                    "html_content": {"type": "string", "description": "HTML内容"},
                    "base_url": {"type": "string", "description": "基础URL", "optional": True}
                },
                "required": ["html_content"]
            },
            returns={
                "type": "object",
                "properties": {
                    "links": {
                        "type": "array",
                        "items": {
                            "type": "object",
                            "properties": {
                                "url": {"type": "string", "description": "链接URL"},
                                "text": {"type": "string", "description": "链接文本"}
                            }
                        }
                    }
                }
            }
        )
        
        # 提取网页元数据工具
        self.register_tool(
            name="extract_metadata",
            func=self._extract_metadata,
            description="从HTML内容中提取元数据",
            parameters={
                "type": "object",
                "properties": {
                    "html_content": {"type": "string", "description": "HTML内容"},
                },
                "required": ["html_content"]
            },
            returns={
                "type": "object",
                "properties": {
                    "metadata": {"type": "object", "description": "元数据字典"}
                }
            }
        )
        
        # 搜索网页内容工具
        self.register_tool(
            name="search_content",
            func=self._search_content,
            description="在HTML内容中搜索特定文本",
            parameters={
                "type": "object",
                "properties": {
                    "html_content": {"type": "string", "description": "HTML内容"},
                    "query": {"type": "string", "description": "搜索关键词"},
                },
                "required": ["html_content", "query"]
            },
            returns={
                "type": "object",
                "properties": {
                    "results": {
                        "type": "array",
                        "items": {"type": "string"},
                        "description": "包含搜索词的段落列表"
                    }
                }
            }
        )
        
        # 一站式网页内容获取工具
        self.register_tool(
            name="fetch_and_extract",
            func=self._fetch_and_extract,
            description="获取网页并提取内容（标题、文本、链接等）",
            parameters={
                "type": "object",
                "properties": {
                    "url": {"type": "string", "description": "网页URL"},
                    "extract_title": {"type": "boolean", "description": "是否提取标题", "optional": True},
                    "extract_text": {"type": "boolean", "description": "是否提取文本", "optional": True},
                    "extract_links": {"type": "boolean", "description": "是否提取链接", "optional": True},
                    "extract_metadata": {"type": "boolean", "description": "是否提取元数据", "optional": True}
                },
                "required": ["url"]
            },
            returns={
                "type": "object",
                "properties": {
                    "url": {"type": "string", "description": "请求的URL"},
                    "title": {"type": "string", "description": "网页标题"},
                    "text": {"type": "string", "description": "提取的文本内容"},
                    "links": {
                        "type": "array",
                        "items": {
                            "type": "object",
                            "properties": {
                                "url": {"type": "string"},
                                "text": {"type": "string"}
                            }
                        },
                        "description": "提取的链接列表"
                    },
                    "metadata": {"type": "object", "description": "元数据字典"}
                }
            }
        )
    
    def get_schema(self) -> Dict[str, Any]:
        """
        获取协议的JSON Schema
        
        Returns:
            描述协议结构的JSON Schema字典
        """
        schema = {
            "type": "object",
            "properties": {
                "protocol": {
                    "type": "object",
                    "properties": {
                        "name": {"type": "string", "enum": [self.name]},
                        "version": {"type": "string", "enum": [self.version]}
                    },
                    "required": ["name", "version"]
                },
                "tool": {
                    "type": "object",
                    "properties": {
                        "name": {"type": "string", "enum": list(self.tools.keys())},
                        "parameters": {"type": "object"}
                    },
                    "required": ["name", "parameters"]
                },
                "metadata": {
                    "type": "object",
                    "properties": {
                        "request_id": {"type": "string"},
                        "timestamp": {"type": "string", "format": "date-time"}
                    }
                }
            },
            "required": ["protocol", "tool"]
        }
        return schema
    
    # 工具实现方法
    
    def _get_page(self, url: str, params: Dict = None) -> Dict[str, str]:
        """
        获取网页内容
        
        Args:
            url: 网页URL
            params: 请求参数
            
        Returns:
            包含网页内容和URL的字典
        """
        content = self.scraper.get_page(url, params)
        return {
            "content": content if content else "",
            "url": url
        }
    
    def _extract_title(self, html_content: str) -> Dict[str, str]:
        """
        从HTML内容中提取标题
        
        Args:
            html_content: HTML内容
            
        Returns:
            包含标题的字典
        """
        title = self.scraper.extract_title(html_content)
        return {
            "title": title if title else ""
        }
    
    def _extract_text(self, html_content: str) -> Dict[str, str]:
        """
        从HTML内容中提取纯文本
        
        Args:
            html_content: HTML内容
            
        Returns:
            包含文本内容的字典
        """
        text = self.scraper.extract_text(html_content)
        return {
            "text": text
        }
    
    def _extract_links(self, html_content: str, base_url: str = "") -> Dict[str, List[Dict[str, str]]]:
        """
        从HTML内容中提取所有链接
        
        Args:
            html_content: HTML内容
            base_url: 基础URL
            
        Returns:
            包含链接列表的字典
        """
        links = self.scraper.extract_links(html_content, base_url)
        return {
            "links": links
        }
    
    def _extract_metadata(self, html_content: str) -> Dict[str, Dict[str, str]]:
        """
        从HTML内容中提取元数据
        
        Args:
            html_content: HTML内容
            
        Returns:
            包含元数据的字典
        """
        metadata = self.scraper.extract_metadata(html_content)
        return {
            "metadata": metadata
        }
    
    def _search_content(self, html_content: str, query: str) -> Dict[str, List[str]]:
        """
        在HTML内容中搜索特定文本
        
        Args:
            html_content: HTML内容
            query: 搜索关键词
            
        Returns:
            包含搜索结果的字典
        """
        results = self.scraper.search_content(html_content, query)
        return {
            "results": results
        }
    
    def _fetch_and_extract(self, url: str, extract_title: bool = True, 
                          extract_text: bool = True, extract_links: bool = True, 
                          extract_metadata: bool = False) -> Dict[str, Any]:
        """
        获取网页并提取内容
        
        Args:
            url: 网页URL
            extract_title: 是否提取标题
            extract_text: 是否提取文本
            extract_links: 是否提取链接
            extract_metadata: 是否提取元数据
            
        Returns:
            包含提取内容的字典
        """
        result = {"url": url}
        
        # 获取网页内容
        page_result = self._get_page(url)
        html_content = page_result["content"]
        
        if not html_content:
            return {
                "url": url,
                "error": "Failed to get page content"
            }
        
        # 根据需要提取各种内容
        if extract_title:
            result["title"] = self._extract_title(html_content)["title"]
        
        if extract_text:
            result["text"] = self._extract_text(html_content)["text"]
        
        if extract_links:
            result["links"] = self._extract_links(html_content, url)["links"]
        
        if extract_metadata:
            result["metadata"] = self._extract_metadata(html_content)["metadata"]
        
        return result 