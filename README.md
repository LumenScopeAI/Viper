# VIPER (Visual Intelligent Protocol Execution Runtime)

VIPER是一个基于分层架构设计的智能协议执行运行时框架，采用严格的分层原则，确保各层之间的清晰边界和责任划分。

## 架构概述

VIPER架构分为四个主要层次：

```mermaid
flowchart TB
subgraph TL[工具层 (Tools Layer)]
  D[RPA 多模态解析 数据处理 通用功能封装]
end
subgraph PL[协议层 (Protocol Layer)]
  C[统一协议 鉴权与访问控制 跨系统适配]
end
subgraph CL[编排层 (Orchestration Layer)]
  B[多智能体 工作流编排 监控与容错 动态调度]
end
subgraph VL[可视化层 (Visualization Layer)]
  A[可视化界面 监控与统计 用户交互]
end

D --> C
C --> B
B --> A
```

### 各层说明

1. **工具层 (Tools Layer)**:
   - 提供基础功能和服务
   - 包括RPA、多模态解析、数据处理等
   - 完全独立于上层，不依赖其他层

2. **协议层 (Protocol Layer)**:
   - 将工具层包装为统一的MCP协议接口
   - 实现跨系统的适配和兼容
   - 提供一致的接口给上层使用

3. **编排层 (Orchestration Layer)**:
   - 基于大语言模型实现多智能体协作
   - 负责工作流编排和任务调度
   - 监控执行过程并处理异常

4. **可视化层 (Visualization Layer)**:
   - 提供用户界面和可视化工具
   - 实时监控和统计系统运行状态
   - 支持用户交互和操作

## 开发原则

- **分层职责**：每层有明确的职责边界，不允许跨层调用
- **向下依赖**：上层可以依赖下层，但下层不能依赖上层
- **分层测试**：每层独立测试，测试时只允许修改该层代码
- **接口稳定**：层间通过稳定接口通信，内部实现可独立变化

## 开发流程

1. 分析应用场景和业务需求
2. 分解业务为所需协议
3. 检查已有协议是否可复用
   - 若可复用，直接使用现有协议开发编排层
   - 若不可复用，开发新协议
     - 检查工具层是否有可复用工具
     - 若可复用，使用现有工具开发协议
     - 若不可复用，先开发并测试新工具

## 安装与使用

### 环境要求

- Python 3.8+
- 依赖库（详见requirements.txt）

### 安装步骤

```bash
# 克隆仓库
git clone https://github.com/yourusername/VIPER.git
cd VIPER

# 创建虚拟环境
python -m venv venv
source venv/bin/activate  # Windows: venv\Scripts\activate

# 安装依赖
pip install -r requirements.txt
```

### 基本使用

1. 启动协议服务
```bash
python -m protocols.server
```

2. 运行编排层示例
```bash
python -m orchestration.examples.simple_workflow
```

3. 启动可视化界面
```bash
python -m visualization.app
```

## 目录结构

```
VIPER/
├── tools/              # 工具层
├── protocols/          # 协议层
├── orchestration/      # 编排层
├── visualization/      # 可视化层
├── tests/              # 测试目录
├── examples/           # 示例代码
├── docs/               # 文档
├── requirements.txt    # 依赖库列表
└── README.md           # 项目说明
```

## 贡献指南

欢迎贡献代码或提出建议。请确保：

1. 遵循分层架构原则，不进行跨层调用
2. 添加适当的测试用例
3. 更新相关文档
4. 提交前运行测试确保通过

## 许可证

[MIT License](LICENSE) 