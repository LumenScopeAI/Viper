"""
智能体管理器 - 管理和协调多个智能体
"""

import json
import uuid
import time
import logging
from typing import Dict, List, Optional, Union, Any, Tuple, Callable

from orchestration.agent import Agent
from orchestration.llm_agent import LLMAgent


# 配置日志
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    handlers=[
        logging.StreamHandler(),
        logging.FileHandler("agents_manager.log")
    ]
)

logger = logging.getLogger("AgentsManager")


class AgentsManager:
    """
    智能体管理器，负责管理和协调多个智能体
    
    提供创建、获取、删除智能体的功能，以及智能体之间的消息传递。
    """
    
    def __init__(self):
        """初始化智能体管理器"""
        self.agents = {}  # 智能体字典，键为智能体ID
        self.agent_types = {
            "llm": LLMAgent
        }  # 注册的智能体类型
        self.messages = []  # 消息记录
        self.callbacks = {}  # 回调函数
    
    def register_agent_type(self, type_name: str, agent_class: type) -> None:
        """
        注册智能体类型
        
        Args:
            type_name: 类型名称
            agent_class: 智能体类
        """
        if not issubclass(agent_class, Agent):
            raise TypeError(f"Agent class must be a subclass of Agent, got {agent_class}")
        
        self.agent_types[type_name] = agent_class
        logger.info(f"已注册智能体类型: {type_name}")
    
    def create_agent(self, agent_type: str, name: str, description: str = "", **kwargs) -> str:
        """
        创建智能体
        
        Args:
            agent_type: 智能体类型
            name: 智能体名称
            description: 智能体描述
            **kwargs: 额外参数
            
        Returns:
            智能体ID
        """
        if agent_type not in self.agent_types:
            raise ValueError(f"Unknown agent type: {agent_type}")
        
        agent_class = self.agent_types[agent_type]
        agent = agent_class(name=name, description=description, **kwargs)
        
        self.agents[agent.id] = agent
        
        # 触发回调
        self.trigger_callback("agent_created", agent_id=agent.id, agent_type=agent_type, agent_name=name)
        
        logger.info(f"已创建智能体: {name} (ID: {agent.id}, 类型: {agent_type})")
        return agent.id
    
    def get_agent(self, agent_id: str) -> Optional[Agent]:
        """
        获取智能体
        
        Args:
            agent_id: 智能体ID
            
        Returns:
            智能体对象
        """
        return self.agents.get(agent_id)
    
    def delete_agent(self, agent_id: str) -> bool:
        """
        删除智能体
        
        Args:
            agent_id: 智能体ID
            
        Returns:
            是否成功删除
        """
        if agent_id in self.agents:
            agent = self.agents[agent_id]
            del self.agents[agent_id]
            
            # 触发回调
            self.trigger_callback("agent_deleted", agent_id=agent_id, agent_name=agent.name)
            
            logger.info(f"已删除智能体: {agent.name} (ID: {agent_id})")
            return True
        
        return False
    
    def list_agents(self) -> List[Dict[str, Any]]:
        """
        列出所有智能体
        
        Returns:
            智能体信息列表
        """
        return [
            {
                "id": agent.id,
                "name": agent.name,
                "description": agent.description,
                "type": agent.__class__.__name__
            }
            for agent in self.agents.values()
        ]
    
    def send_message(self, from_agent_id: str, to_agent_id: str, 
                   content: Any, message_type: str = "text") -> str:
        """
        发送消息
        
        Args:
            from_agent_id: 发送方智能体ID
            to_agent_id: 接收方智能体ID
            content: 消息内容
            message_type: 消息类型
            
        Returns:
            消息ID
        """
        if from_agent_id not in self.agents:
            raise ValueError(f"Unknown from_agent_id: {from_agent_id}")
        
        if to_agent_id not in self.agents:
            raise ValueError(f"Unknown to_agent_id: {to_agent_id}")
        
        message_id = str(uuid.uuid4())
        timestamp = time.time()
        
        message = {
            "id": message_id,
            "from": from_agent_id,
            "to": to_agent_id,
            "content": content,
            "type": message_type,
            "timestamp": timestamp
        }
        
        self.messages.append(message)
        
        # 触发回调
        self.trigger_callback("message_sent", 
                           message=message, 
                           from_agent=self.agents[from_agent_id].name,
                           to_agent=self.agents[to_agent_id].name)
        
        logger.info(f"消息从 {self.agents[from_agent_id].name} 发送到 {self.agents[to_agent_id].name}: {content[:50]}...")
        return message_id
    
    def get_messages(self, agent_id: str = None, start_time: float = None, 
                    end_time: float = None, message_type: str = None, 
                    limit: int = 100) -> List[Dict[str, Any]]:
        """
        获取消息
        
        Args:
            agent_id: 智能体ID，获取与该智能体相关的消息
            start_time: 开始时间戳
            end_time: 结束时间戳
            message_type: 消息类型
            limit: 返回消息数量限制
            
        Returns:
            消息列表
        """
        filtered = self.messages
        
        if agent_id:
            filtered = [m for m in filtered if m["from"] == agent_id or m["to"] == agent_id]
        
        if start_time:
            filtered = [m for m in filtered if m["timestamp"] >= start_time]
        
        if end_time:
            filtered = [m for m in filtered if m["timestamp"] <= end_time]
        
        if message_type:
            filtered = [m for m in filtered if m["type"] == message_type]
        
        # 按时间戳排序
        filtered.sort(key=lambda m: m["timestamp"], reverse=True)
        
        return filtered[:limit]
    
    def get_conversation(self, agent1_id: str, agent2_id: str, 
                       limit: int = 100) -> List[Dict[str, Any]]:
        """
        获取两个智能体之间的对话
        
        Args:
            agent1_id: 第一个智能体ID
            agent2_id: 第二个智能体ID
            limit: 返回消息数量限制
            
        Returns:
            消息列表
        """
        conversation = [
            m for m in self.messages 
            if (m["from"] == agent1_id and m["to"] == agent2_id) or 
               (m["from"] == agent2_id and m["to"] == agent1_id)
        ]
        
        # 按时间戳排序
        conversation.sort(key=lambda m: m["timestamp"])
        
        return conversation[-limit:]
    
    def simulate_conversation(self, agent1_id: str, agent2_id: str, 
                           initial_message: str, max_turns: int = 5) -> List[Dict[str, Any]]:
        """
        模拟两个智能体之间的对话
        
        Args:
            agent1_id: 第一个智能体ID
            agent2_id: 第二个智能体ID
            initial_message: 初始消息
            max_turns: 最大对话轮数
            
        Returns:
            对话消息列表
        """
        agent1 = self.get_agent(agent1_id)
        agent2 = self.get_agent(agent2_id)
        
        if not agent1 or not agent2:
            raise ValueError(f"Agent not found: {agent1_id if not agent1 else agent2_id}")
        
        # 发送初始消息
        current_message = initial_message
        current_sender = agent1_id
        current_receiver = agent2_id
        
        for _ in range(max_turns):
            # 发送消息
            message_id = self.send_message(
                from_agent_id=current_sender,
                to_agent_id=current_receiver,
                content=current_message
            )
            
            # 接收方处理消息
            receiver = self.get_agent(current_receiver)
            response = receiver.run(current_message)
            
            if isinstance(response, dict) and "result" in response:
                response_content = response["result"]
            else:
                response_content = str(response)
            
            # 交换发送方和接收方
            current_sender, current_receiver = current_receiver, current_sender
            current_message = response_content
        
        # 返回对话
        return self.get_conversation(agent1_id, agent2_id)
    
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
    
    def get_stats(self) -> Dict[str, Any]:
        """
        获取统计信息
        
        Returns:
            统计信息字典
        """
        return {
            "agent_count": len(self.agents),
            "message_count": len(self.messages),
            "agent_types": list(self.agent_types.keys())
        } 