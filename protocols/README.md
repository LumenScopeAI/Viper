# 协议层 (Protocol Layer)

协议层是VIPER架构中的关键层，负责将底层工具封装为统一的MCP（Model Context Protocol）协议格式，提供一致的接口供上层编排使用。

## 职责

- 将不同接口的工具类转换为统一的MCP协议格式
- 实现跨系统的适配和兼容
- 提供鉴权与访问控制机制
- 处理协议级别的错误和异常

## MCP协议说明

MCP（Model Context Protocol）是一种标准化协议，用于定义AI模型与外部工具和服务的交互方式。本层实现遵循MCP协议规范，提供以下核心功能：

- Resources：资源定义和管理
- Tools：工具定义和调用接口
- Prompts：提示词管理
- Sampling：采样策略
- Roots：根目录结构
- Transports：传输层实现（stdio和SSE）

## 协议列表

- `web_protocol.py`: 网络访问和搜索协议，封装web_scraper工具
- `file_protocol.py`: 文件处理协议，封装file_handler工具
- `image_protocol.py`: 图像处理协议，封装image_processor工具
- `data_protocol.py`: 数据转换协议，封装data_transformer工具

## 开发规范

1. 所有协议必须严格遵循MCP协议规范
2. 协议接口应当隐藏底层工具的具体实现细节
3. 每个协议必须有明确的版本和兼容性说明
4. 协议层必须做好访问控制和安全检查
5. 应提供详细的协议文档，说明每个方法的用途、参数和返回值格式 