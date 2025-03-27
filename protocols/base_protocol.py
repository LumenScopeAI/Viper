"""
基础协议类 - 遵循MCP协议规范的基本实现
"""

import json
import uuid
from typing import Dict, List, Optional, Union, Any, Callable
from abc import ABC, abstractmethod


class BaseProtocol(ABC):
    """
    基础协议抽象类，定义了MCP协议的基本结构和接口
    
    遵循MCP协议标准，提供以下核心功能:
    1. 资源定义和管理 (Resources)
    2. 工具定义和调用 (Tools)
    3. 协议头与元数据处理
    """
    
    def __init__(self, name: str, version: str = "1.0.0", description: str = ""):
        """
        初始化基础协议
        
        Args:
            name: 协议名称
            version: 协议版本
            description: 协议描述
        """
        self.name = name
        self.version = version
        self.description = description
        self.tools = {}  # 工具注册表
        self.resources = {}  # 资源注册表
    
    @abstractmethod
    def get_schema(self) -> Dict[str, Any]:
        """
        获取协议的JSON Schema
        
        Returns:
            描述协议结构的JSON Schema字典
        """
        pass
    
    def register_tool(self, name: str, func: Callable, description: str, 
                      parameters: Dict[str, Any], returns: Dict[str, Any]) -> None:
        """
        注册工具
        
        Args:
            name: 工具名称
            func: 工具函数
            description: 工具描述
            parameters: 参数定义
            returns: 返回值定义
        """
        self.tools[name] = {
            "func": func,
            "description": description,
            "parameters": parameters,
            "returns": returns
        }
    
    def execute_tool(self, name: str, **kwargs) -> Dict[str, Any]:
        """
        执行工具
        
        Args:
            name: 要执行的工具名称
            **kwargs: 工具参数
            
        Returns:
            工具执行结果
        """
        if name not in self.tools:
            return {
                "error": f"Tool '{name}' not found",
                "status": "error"
            }
        
        try:
            tool = self.tools[name]
            result = tool["func"](**kwargs)
            return {
                "data": result,
                "status": "success"
            }
        except Exception as e:
            return {
                "error": str(e),
                "status": "error"
            }
    
    def register_resource(self, name: str, resource_type: str, 
                         data: Any, description: str = "") -> str:
        """
        注册资源
        
        Args:
            name: 资源名称
            resource_type: 资源类型
            data: 资源数据
            description: 资源描述
            
        Returns:
            资源ID
        """
        resource_id = str(uuid.uuid4())
        self.resources[resource_id] = {
            "name": name,
            "type": resource_type,
            "data": data,
            "description": description
        }
        return resource_id
    
    def get_resource(self, resource_id: str) -> Optional[Dict[str, Any]]:
        """
        获取资源
        
        Args:
            resource_id: 资源ID
            
        Returns:
            资源数据，如果资源不存在则返回None
        """
        return self.resources.get(resource_id)
    
    def format_mcp_request(self, tool_name: str, **kwargs) -> Dict[str, Any]:
        """
        格式化MCP请求
        
        Args:
            tool_name: 工具名称
            **kwargs: 工具参数
            
        Returns:
            符合MCP协议的请求字典
        """
        return {
            "protocol": {
                "name": self.name,
                "version": self.version
            },
            "tool": {
                "name": tool_name,
                "parameters": kwargs
            },
            "metadata": {
                "request_id": str(uuid.uuid4()),
                "timestamp": import_time()
            }
        }
    
    def format_mcp_response(self, request: Dict[str, Any], 
                          result: Any, status: str = "success", 
                          error: str = None) -> Dict[str, Any]:
        """
        格式化MCP响应
        
        Args:
            request: 原始请求
            result: 结果数据
            status: 状态，"success"或"error"
            error: 错误信息
            
        Returns:
            符合MCP协议的响应字典
        """
        response = {
            "protocol": {
                "name": self.name,
                "version": self.version
            },
            "metadata": {
                "request_id": request.get("metadata", {}).get("request_id", str(uuid.uuid4())),
                "timestamp": import_time(),
                "status": status
            },
            "result": result
        }
        
        if error:
            response["error"] = error
            
        return response


def import_time():
    """获取当前时间戳"""
    from datetime import datetime
    return datetime.now().isoformat()