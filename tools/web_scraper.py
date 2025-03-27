"""
网页抓取工具 - 提供网页内容获取和解析功能
"""

import re
import json
import requests
from typing import Dict, List, Optional, Union, Any
from urllib.parse import urlparse
from bs4 import BeautifulSoup


class WebScraper:
    """
    网页抓取工具类，提供网页内容获取和解析功能
    
    该类提供以下功能:
    1. 获取网页内容
    2. 解析网页标题、正文、链接等内容
    3. 支持内容提取和筛选
    """
    
    def __init__(self, user_agent: str = None, timeout: int = 10):
        """
        初始化WebScraper
        
        Args:
            user_agent: 请求头中的User-Agent
            timeout: 请求超时时间(秒)
        """
        self.user_agent = user_agent or "VIPER WebScraper/0.1.0"
        self.timeout = timeout
        self.session = requests.Session()
        self.headers = {
            "User-Agent": self.user_agent
        }
    
    def get_page(self, url: str, params: Dict = None) -> Optional[str]:
        """
        获取网页内容
        
        Args:
            url: 网页URL
            params: 请求参数
            
        Returns:
            网页内容文本，如果获取失败则返回None
        """
        try:
            response = self.session.get(
                url, 
                headers=self.headers, 
                params=params,
                timeout=self.timeout
            )
            response.raise_for_status()
            return response.text
        except requests.RequestException as e:
            print(f"获取网页内容失败: {e}")
            return None
    
    def extract_title(self, html_content: str) -> Optional[str]:
        """
        从HTML内容中提取标题
        
        Args:
            html_content: HTML内容
            
        Returns:
            网页标题，如果提取失败则返回None
        """
        try:
            soup = BeautifulSoup(html_content, 'html.parser')
            title = soup.title.string if soup.title else None
            return title.strip() if title else None
        except Exception as e:
            print(f"提取标题失败: {e}")
            return None
    
    def extract_text(self, html_content: str) -> str:
        """
        从HTML内容中提取纯文本
        
        Args:
            html_content: HTML内容
            
        Returns:
            提取的纯文本内容
        """
        try:
            soup = BeautifulSoup(html_content, 'html.parser')
            
            # 移除script和style元素
            for script in soup(["script", "style"]):
                script.extract()
            
            # 获取文本
            text = soup.get_text()
            
            # 处理多余的空白字符
            lines = (line.strip() for line in text.splitlines())
            chunks = (phrase.strip() for line in lines for phrase in line.split("  "))
            text = '\n'.join(chunk for chunk in chunks if chunk)
            
            return text
        except Exception as e:
            print(f"提取文本失败: {e}")
            return ""
    
    def extract_links(self, html_content: str, base_url: str = "") -> List[Dict[str, str]]:
        """
        从HTML内容中提取所有链接
        
        Args:
            html_content: HTML内容
            base_url: 基础URL，用于处理相对链接
            
        Returns:
            链接列表，每个链接包含url和text两个字段
        """
        try:
            soup = BeautifulSoup(html_content, 'html.parser')
            links = []
            
            for a_tag in soup.find_all('a', href=True):
                href = a_tag['href']
                # 处理相对链接
                if base_url and not bool(urlparse(href).netloc):
                    href = base_url.rstrip('/') + '/' + href.lstrip('/')
                
                links.append({
                    'url': href,
                    'text': a_tag.get_text().strip()
                })
            
            return links
        except Exception as e:
            print(f"提取链接失败: {e}")
            return []
    
    def extract_metadata(self, html_content: str) -> Dict[str, str]:
        """
        从HTML内容中提取元数据
        
        Args:
            html_content: HTML内容
            
        Returns:
            元数据字典
        """
        try:
            soup = BeautifulSoup(html_content, 'html.parser')
            metadata = {}
            
            # 提取meta标签信息
            for meta in soup.find_all('meta'):
                if meta.get('name'):
                    metadata[meta.get('name')] = meta.get('content', '')
                elif meta.get('property'):
                    metadata[meta.get('property')] = meta.get('content', '')
            
            return metadata
        except Exception as e:
            print(f"提取元数据失败: {e}")
            return {}
    
    def search_content(self, html_content: str, query: str) -> List[str]:
        """
        在HTML内容中搜索特定文本
        
        Args:
            html_content: HTML内容
            query: 搜索关键词
            
        Returns:
            包含搜索词的段落列表
        """
        try:
            text = self.extract_text(html_content)
            paragraphs = text.split('\n')
            results = []
            
            for paragraph in paragraphs:
                if query.lower() in paragraph.lower():
                    results.append(paragraph)
            
            return results
        except Exception as e:
            print(f"搜索内容失败: {e}")
            return [] 