"""
工作流引擎 - 编排任务执行流程
"""

import json
import time
import uuid
from typing import Dict, List, Optional, Union, Any, Tuple, Callable
from enum import Enum

from orchestration.agent import Agent


class TaskStatus(Enum):
    """任务状态枚举"""
    PENDING = "pending"
    RUNNING = "running"
    COMPLETED = "completed"
    FAILED = "failed"
    CANCELLED = "cancelled"


class Task:
    """
    任务类，表示工作流中的一个任务节点
    """
    
    def __init__(self, name: str, description: str = "", agent: Agent = None,
               inputs: Dict[str, Any] = None, dependencies: List[str] = None):
        """
        初始化任务
        
        Args:
            name: 任务名称
            description: 任务描述
            agent: 执行任务的智能体
            inputs: 任务输入参数
            dependencies: 依赖任务ID列表
        """
        self.id = str(uuid.uuid4())
        self.name = name
        self.description = description
        self.agent = agent
        self.inputs = inputs or {}
        self.dependencies = dependencies or []
        self.status = TaskStatus.PENDING
        self.result = None
        self.error = None
        self.start_time = None
        self.end_time = None
    
    def execute(self, context: Dict[str, Any] = None) -> Dict[str, Any]:
        """
        执行任务
        
        Args:
            context: 任务上下文
            
        Returns:
            任务执行结果
        """
        if not self.agent:
            self.status = TaskStatus.FAILED
            self.error = "No agent assigned"
            return {"error": self.error}
        
        self.status = TaskStatus.RUNNING
        self.start_time = time.time()
        
        try:
            inputs = {**self.inputs, **(context or {})}
            prompt = self._generate_prompt(inputs)
            self.result = self.agent.run(prompt, inputs)
            self.status = TaskStatus.COMPLETED
        except Exception as e:
            self.status = TaskStatus.FAILED
            self.error = str(e)
            self.result = {"error": self.error}
        
        self.end_time = time.time()
        return self.result
    
    def _generate_prompt(self, inputs: Dict[str, Any]) -> str:
        """
        生成任务提示词
        
        Args:
            inputs: 任务输入参数
            
        Returns:
            提示词文本
        """
        # 基础提示词
        prompt = f"任务: {self.name}\n"
        if self.description:
            prompt += f"描述: {self.description}\n"
        
        # 添加输入参数
        if inputs:
            prompt += "\n输入参数:\n"
            for key, value in inputs.items():
                if isinstance(value, (dict, list)):
                    prompt += f"{key}: {json.dumps(value, ensure_ascii=False)}\n"
                else:
                    prompt += f"{key}: {value}\n"
        
        return prompt
    
    def cancel(self) -> None:
        """取消任务"""
        if self.status == TaskStatus.PENDING or self.status == TaskStatus.RUNNING:
            self.status = TaskStatus.CANCELLED
            self.end_time = time.time()
    
    def get_state(self) -> Dict[str, Any]:
        """
        获取任务状态
        
        Returns:
            任务状态字典
        """
        return {
            "id": self.id,
            "name": self.name,
            "description": self.description,
            "status": self.status.value,
            "agent": self.agent.name if self.agent else None,
            "dependencies": self.dependencies,
            "start_time": self.start_time,
            "end_time": self.end_time,
            "duration": self.end_time - self.start_time if self.start_time and self.end_time else None,
            "result": self.result,
            "error": self.error
        }
    

class Workflow:
    """
    工作流类，管理任务依赖和执行顺序
    """
    
    def __init__(self, name: str, description: str = ""):
        """
        初始化工作流
        
        Args:
            name: 工作流名称
            description: 工作流描述
        """
        self.id = str(uuid.uuid4())
        self.name = name
        self.description = description
        self.tasks = {}  # 任务字典，键为任务ID
        self.status = TaskStatus.PENDING
        self.context = {}  # 工作流上下文
        self.start_time = None
        self.end_time = None
        self.callbacks = {}  # 回调函数
    
    def add_task(self, task: Task) -> str:
        """
        添加任务到工作流
        
        Args:
            task: 任务对象
            
        Returns:
            任务ID
        """
        self.tasks[task.id] = task
        return task.id
    
    def remove_task(self, task_id: str) -> bool:
        """
        从工作流中移除任务
        
        Args:
            task_id: 任务ID
            
        Returns:
            是否成功移除
        """
        if task_id in self.tasks:
            # 检查是否有任务依赖于此任务
            for other_task in self.tasks.values():
                if task_id in other_task.dependencies:
                    return False
            
            del self.tasks[task_id]
            return True
        
        return False
    
    def get_task(self, task_id: str) -> Optional[Task]:
        """
        获取任务
        
        Args:
            task_id: 任务ID
            
        Returns:
            任务对象
        """
        return self.tasks.get(task_id)
    
    def add_dependency(self, task_id: str, depends_on: str) -> bool:
        """
        添加任务依赖
        
        Args:
            task_id: 任务ID
            depends_on: 依赖任务ID
            
        Returns:
            是否成功添加
        """
        if task_id not in self.tasks or depends_on not in self.tasks:
            return False
        
        # 检查是否会形成循环依赖
        if self._would_form_cycle(task_id, depends_on):
            return False
        
        self.tasks[task_id].dependencies.append(depends_on)
        return True
    
    def _would_form_cycle(self, task_id: str, depends_on: str) -> bool:
        """
        检查添加依赖是否会形成循环
        
        Args:
            task_id: 任务ID
            depends_on: 依赖任务ID
            
        Returns:
            是否会形成循环
        """
        # 如果目标依赖于当前任务，会形成循环
        if task_id == depends_on:
            return True
        
        # 检查依赖链
        visited = set()
        
        def dfs(current_id: str) -> bool:
            if current_id == task_id:
                return True
            
            visited.add(current_id)
            
            for dep_id in self.tasks[current_id].dependencies:
                if dep_id not in visited and dep_id in self.tasks:
                    if dfs(dep_id):
                        return True
            
            return False
        
        return dfs(depends_on)
    
    def get_executable_tasks(self) -> List[Task]:
        """
        获取当前可执行的任务
        
        Returns:
            可执行任务列表
        """
        executable = []
        
        for task in self.tasks.values():
            if task.status == TaskStatus.PENDING:
                # 检查依赖是否都已完成
                all_deps_completed = True
                for dep_id in task.dependencies:
                    if dep_id not in self.tasks or self.tasks[dep_id].status != TaskStatus.COMPLETED:
                        all_deps_completed = False
                        break
                
                if all_deps_completed:
                    executable.append(task)
        
        return executable
    
    def execute(self) -> Dict[str, Any]:
        """
        执行工作流
        
        Returns:
            工作流执行结果
        """
        self.status = TaskStatus.RUNNING
        self.start_time = time.time()
        
        self.trigger_callback("workflow_started")
        
        try:
            # 执行任务直到所有任务完成或失败
            while True:
                executable_tasks = self.get_executable_tasks()
                
                if not executable_tasks:
                    # 检查是否所有任务都已完成
                    all_completed = True
                    for task in self.tasks.values():
                        if task.status != TaskStatus.COMPLETED and task.status != TaskStatus.FAILED and task.status != TaskStatus.CANCELLED:
                            all_completed = False
                            break
                    
                    if all_completed:
                        break
                    
                    # 如果没有可执行任务但还有未完成任务，可能存在死锁
                    pending_tasks = [t for t in self.tasks.values() if t.status == TaskStatus.PENDING]
                    if pending_tasks:
                        raise RuntimeError("Deadlock detected: There are pending tasks but none can be executed.")
                
                # 执行可执行任务
                for task in executable_tasks:
                    # 准备任务上下文，包含依赖任务的结果
                    task_context = {**self.context}
                    for dep_id in task.dependencies:
                        if dep_id in self.tasks and self.tasks[dep_id].result:
                            task_context[f"task_{dep_id}_result"] = self.tasks[dep_id].result
                    
                    # 触发任务开始回调
                    self.trigger_callback("task_started", task_id=task.id, task_name=task.name)
                    
                    # 执行任务
                    result = task.execute(task_context)
                    
                    # 将任务结果添加到工作流上下文
                    self.context[f"task_{task.id}_result"] = result
                    
                    # 触发任务完成或失败回调
                    if task.status == TaskStatus.COMPLETED:
                        self.trigger_callback("task_completed", task_id=task.id, task_name=task.name, result=result)
                    else:  # FAILED
                        self.trigger_callback("task_failed", task_id=task.id, task_name=task.name, error=task.error)
            
            # 确定工作流状态
            if any(task.status == TaskStatus.FAILED for task in self.tasks.values()):
                self.status = TaskStatus.FAILED
            else:
                self.status = TaskStatus.COMPLETED
        
        except Exception as e:
            self.status = TaskStatus.FAILED
            self.trigger_callback("workflow_error", error=str(e))
        
        self.end_time = time.time()
        
        # 触发工作流完成或失败回调
        if self.status == TaskStatus.COMPLETED:
            self.trigger_callback("workflow_completed", results=self.get_results())
        else:
            self.trigger_callback("workflow_failed")
        
        return self.get_results()
    
    def cancel(self) -> None:
        """取消工作流"""
        if self.status == TaskStatus.PENDING or self.status == TaskStatus.RUNNING:
            self.status = TaskStatus.CANCELLED
            self.end_time = time.time()
            
            # 取消所有未完成的任务
            for task in self.tasks.values():
                task.cancel()
            
            self.trigger_callback("workflow_cancelled")
    
    def get_results(self) -> Dict[str, Any]:
        """
        获取工作流结果
        
        Returns:
            任务结果字典，键为任务ID
        """
        return {task_id: task.result for task_id, task in self.tasks.items() if task.status == TaskStatus.COMPLETED}
    
    def get_state(self) -> Dict[str, Any]:
        """
        获取工作流状态
        
        Returns:
            工作流状态字典
        """
        return {
            "id": self.id,
            "name": self.name,
            "description": self.description,
            "status": self.status.value,
            "tasks": {task_id: task.get_state() for task_id, task in self.tasks.items()},
            "start_time": self.start_time,
            "end_time": self.end_time,
            "duration": self.end_time - self.start_time if self.start_time and self.end_time else None
        }
    
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