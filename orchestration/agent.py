"""
基础智能体 - 编排层中各种智能体的基类
"""

import json
import uuid
from abc import ABC, abstractmethod
from typing import Dict, List, Optional, Union, Any, Tuple, Callable


class Agent(ABC):
    """
    基础智能体抽象类，定义智能体的基本结构和接口
    
    智能体是编排层中的核心组件，负责执行特定任务，可以与其他智能体协作。
    """
    
    def __init__(self, name: str, description: str = "", model: str = "default"):
        """
        初始化智能体
        
        Args:
            name: 智能体名称
            description: 智能体描述
            model: 使用的语言模型
        """
        self.id = str(uuid.uuid4())
        self.name = name
        self.description = description
        self.model = model
        self.memory = []  # 智能体记忆
        self.tools = {}  # 可用工具集
        self.state = {}  # 智能体状态
        self.callbacks = {}  # 回调函数
    
    @abstractmethod
    def run(self, task: str, context: Dict[str, Any] = None) -> Dict[str, Any]:
        """
        运行智能体处理任务
        
        Args:
            task: 要执行的任务描述
            context: 任务上下文
            
        Returns:
            任务执行结果
        """
        pass
    
    def register_tool(self, name: str, func: Callable, description: str) -> None:
        """
        注册工具
        
        Args:
            name: 工具名称
            func: 工具函数
            description: 工具描述
        """
        self.tools[name] = {
            "func": func,
            "description": description
        }
    
    def use_tool(self, tool_name: str, **kwargs) -> Any:
        """
        使用工具
        
        Args:
            tool_name: 工具名称
            **kwargs: 工具参数
            
        Returns:
            工具执行结果
        """
        if tool_name not in self.tools:
            raise ValueError(f"Tool '{tool_name}' not found")
        
        tool = self.tools[tool_name]
        return tool["func"](**kwargs)
    
    def remember(self, memory_item: Dict[str, Any]) -> None:
        """
        添加记忆
        
        Args:
            memory_item: 记忆项
        """
        self.memory.append(memory_item)
    
    def recall(self, query: str = None, limit: int = 5) -> List[Dict[str, Any]]:
        """
        检索记忆
        
        Args:
            query: 检索查询
            limit: 返回记忆数量限制
            
        Returns:
            相关记忆列表
        """
        if query is None:
            # 如果没有查询，返回最近的记忆
            return self.memory[-limit:]
        
        # 简单的关键词匹配
        matched = []
        for item in self.memory:
            content = json.dumps(item)
            if query.lower() in content.lower():
                matched.append(item)
                if len(matched) >= limit:
                    break
        
        return matched
    
    def clear_memory(self) -> None:
        """清除记忆"""
        self.memory = []
    
    def register_callback(self, event: str, callback: Callable) -> None:
        """
        注册回调函数
        
        Args:
            event: 事件名称
            callback: 回调函数
        """
        if event not in self.callbacks:
            self.callbacks[event] = []
        
        self.callbacks[event].append(callback)
    
    def trigger_callback(self, event: str, **kwargs) -> None:
        """
        触发回调函数
        
        Args:
            event: 事件名称
            **kwargs: 回调参数
        """
        if event in self.callbacks:
            for callback in self.callbacks[event]:
                callback(**kwargs)
    
    def get_state(self) -> Dict[str, Any]:
        """
        获取智能体状态
        
        Returns:
            智能体状态
        """
        return {
            "id": self.id,
            "name": self.name,
            "description": self.description,
            "model": self.model,
            "memory_size": len(self.memory),
            "tools": list(self.tools.keys()),
            "state": self.state
        }
    
    def set_state(self, key: str, value: Any) -> None:
        """
        设置智能体状态
        
        Args:
            key: 状态键
            value: 状态值
        """
        self.state[key] = value
    
    def get_tool_descriptions(self) -> str:
        """
        获取工具描述
        
        Returns:
            工具描述文本
        """
        descriptions = []
        for name, tool in self.tools.items():
            descriptions.append(f"{name}: {tool['description']}")
        
        return "\n".join(descriptions)
    
    def __repr__(self) -> str:
        """获取智能体字符串表示"""
        return f"Agent(id={self.id}, name={self.name}, model={self.model})" 