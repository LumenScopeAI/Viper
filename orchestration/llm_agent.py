"""
LLM智能体 - 基于大语言模型的智能体实现
"""

import json
import re
import os
import time
import requests
from typing import Dict, List, Optional, Union, Any, Tuple, Callable

from orchestration.agent import Agent


class LLMAgent(Agent):
    """
    基于大语言模型的智能体实现
    
    使用大语言模型进行推理和决策，可以使用各种工具来完成任务。
    """
    
    def __init__(self, name: str, description: str = "", 
                model: str = "gpt-4", api_key: str = None,
                base_url: str = "https://api.openai.com/v1",
                system_prompt: str = None):
        """
        初始化LLM智能体
        
        Args:
            name: 智能体名称
            description: 智能体描述
            model: 使用的语言模型
            api_key: OpenAI API密钥
            base_url: API基础URL
            system_prompt: 系统提示词
        """
        super().__init__(name, description, model)
        
        # API配置
        self.api_key = api_key or os.environ.get("OPENAI_API_KEY")
        self.base_url = base_url
        
        # 默认系统提示词
        self.system_prompt = system_prompt or f"""你是一个名为{name}的智能体。
{description}

你可以使用以下工具来完成任务:
{{tools}}

请使用JSON格式进行思考，回答和工具调用。
当你需要思考时，使用以下格式:
```thinking
这里是你的思考过程...
```

当你需要调用工具时，使用以下格式:
```tool
{{
  "tool": "工具名称",
  "params": {{
    "参数1": "值1",
    "参数2": "值2"
  }}
}}
```

当你完成任务时，使用以下格式回答:
```response
{{
  "result": "任务结果",
  "summary": "任务总结"
}}
```
"""
        
        # 对话历史
        self.conversation = []
    
    def run(self, task: str, context: Dict[str, Any] = None) -> Dict[str, Any]:
        """
        运行智能体处理任务
        
        Args:
            task: 要执行的任务描述
            context: 任务上下文
            
        Returns:
            任务执行结果
        """
        context = context or {}
        
        # 添加任务到对话历史
        self.conversation.append({
            "role": "user",
            "content": task
        })
        
        # 添加上下文到状态
        for key, value in context.items():
            self.set_state(key, value)
        
        # 最大尝试次数
        max_iterations = 10
        iterations = 0
        
        while iterations < max_iterations:
            iterations += 1
            
            # 调用LLM获取响应
            response = self._call_llm()
            
            # 解析响应
            parsed = self._parse_response(response)
            
            # 添加响应到对话历史
            self.conversation.append({
                "role": "assistant",
                "content": response
            })
            
            # 如果需要调用工具
            if "tool" in parsed:
                tool_result = self._handle_tool_call(parsed["tool"])
                
                # 添加工具结果到对话历史
                self.conversation.append({
                    "role": "user",
                    "content": f"工具 '{parsed['tool']['tool']}' 返回结果: {json.dumps(tool_result, ensure_ascii=False)}"
                })
                
                # 触发回调
                self.trigger_callback("tool_called", 
                                   tool=parsed["tool"]["tool"], 
                                   params=parsed["tool"]["params"], 
                                   result=tool_result)
            
            # 如果有响应结果
            if "response" in parsed:
                # 添加记忆
                self.remember({
                    "task": task,
                    "context": context,
                    "response": parsed["response"],
                    "timestamp": time.time()
                })
                
                # 触发回调
                self.trigger_callback("task_completed", 
                                   task=task, 
                                   result=parsed["response"])
                
                return parsed["response"]
            
            # 如果有思考过程但没有响应结果，继续迭代
            if "thinking" in parsed:
                # 触发回调
                self.trigger_callback("thinking", 
                                   thoughts=parsed["thinking"])
        
        # 如果达到最大迭代次数，返回超时信息
        timeout_response = {
            "result": "Timeout",
            "summary": f"达到最大迭代次数({max_iterations})，任务未完成"
        }
        
        # 添加记忆
        self.remember({
            "task": task,
            "context": context,
            "response": timeout_response,
            "timestamp": time.time()
        })
        
        # 触发回调
        self.trigger_callback("task_timeout", 
                           task=task, 
                           iterations=iterations)
        
        return timeout_response
    
    def _call_llm(self) -> str:
        """
        调用大语言模型
        
        Returns:
            模型响应文本
        """
        if not self.api_key:
            raise ValueError("Missing OpenAI API key")
        
        # 构造系统提示词，包含工具描述
        system_prompt = self.system_prompt.format(tools=self.get_tool_descriptions())
        
        # 准备消息
        messages = [
            {"role": "system", "content": system_prompt}
        ] + self.conversation
        
        # 调用API
        url = f"{self.base_url}/chat/completions"
        headers = {
            "Content-Type": "application/json",
            "Authorization": f"Bearer {self.api_key}"
        }
        payload = {
            "model": self.model,
            "messages": messages,
            "temperature": 0.5
        }
        
        try:
            response = requests.post(url, headers=headers, json=payload)
            response.raise_for_status()
            result = response.json()
            return result["choices"][0]["message"]["content"]
        except Exception as e:
            self.trigger_callback("api_error", error=str(e))
            return f"API调用错误: {str(e)}"
    
    def _parse_response(self, response: str) -> Dict[str, Any]:
        """
        解析LLM响应
        
        Args:
            response: LLM响应文本
            
        Returns:
            解析后的响应
        """
        result = {}
        
        # 提取思考过程
        thinking_match = re.search(r'```thinking\n(.*?)\n```', response, re.DOTALL)
        if thinking_match:
            result["thinking"] = thinking_match.group(1).strip()
        
        # 提取工具调用
        tool_match = re.search(r'```tool\n(.*?)\n```', response, re.DOTALL)
        if tool_match:
            try:
                tool_data = json.loads(tool_match.group(1).strip())
                result["tool"] = tool_data
            except json.JSONDecodeError:
                self.trigger_callback("parse_error", 
                                   error="Invalid tool JSON", 
                                   content=tool_match.group(1).strip())
        
        # 提取最终响应
        response_match = re.search(r'```response\n(.*?)\n```', response, re.DOTALL)
        if response_match:
            try:
                response_data = json.loads(response_match.group(1).strip())
                result["response"] = response_data
            except json.JSONDecodeError:
                self.trigger_callback("parse_error", 
                                   error="Invalid response JSON", 
                                   content=response_match.group(1).strip())
        
        return result
    
    def _handle_tool_call(self, tool_data: Dict[str, Any]) -> Any:
        """
        处理工具调用
        
        Args:
            tool_data: 工具调用数据
            
        Returns:
            工具执行结果
        """
        tool_name = tool_data.get("tool")
        params = tool_data.get("params", {})
        
        if not tool_name:
            return {"error": "Missing tool name"}
        
        try:
            return self.use_tool(tool_name, **params)
        except Exception as e:
            error_message = f"Tool execution error: {str(e)}"
            self.trigger_callback("tool_error", 
                              tool=tool_name, 
                              params=params, 
                              error=error_message)
            return {"error": error_message}
    
    def clear_conversation(self) -> None:
        """清除对话历史"""
        self.conversation = [] 