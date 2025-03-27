"""
MCP协议服务器 - 整合所有协议并提供HTTP/STDIO接口
"""

import json
import sys
import os
import logging
import asyncio
import signal
from typing import Dict, List, Optional, Union, Any
from http.server import HTTPServer, BaseHTTPRequestHandler
import threading
import uuid

from protocols.base_protocol import BaseProtocol
from protocols.web_protocol import WebProtocol
from protocols.image_protocol import ImageProtocol


# 配置日志
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    handlers=[
        logging.StreamHandler(),
        logging.FileHandler("mcp_server.log")
    ]
)

logger = logging.getLogger("MCP_Server")


class MCPServer:
    """
    MCP协议服务器，整合各种协议并提供标准输入输出和HTTP接口
    
    遵循MCP协议规范，支持两种传输方式:
    1. STDIO: 通过标准输入输出流进行通信
    2. SSE: 基于HTTP的服务器发送事件
    """
    
    def __init__(self, use_http: bool = False, http_port: int = 8000):
        """
        初始化MCP服务器
        
        Args:
            use_http: 是否使用HTTP服务器
            http_port: HTTP服务器端口
        """
        self.use_http = use_http
        self.http_port = http_port
        self.protocols = {}  # 协议注册表
        self.http_server = None
        self.running = False
        
        # 注册协议
        self._register_protocols()
        
        # 设置信号处理
        signal.signal(signal.SIGINT, self._handle_exit)
        signal.signal(signal.SIGTERM, self._handle_exit)
    
    def _register_protocols(self):
        """注册所有协议"""
        
        # 注册Web协议
        web_protocol = WebProtocol()
        self.protocols[web_protocol.name] = web_protocol
        
        # 注册图像协议
        image_protocol = ImageProtocol()
        self.protocols[image_protocol.name] = image_protocol
        
        # 可以添加更多协议...
        
        logger.info(f"已注册协议: {', '.join(self.protocols.keys())}")
    
    def _handle_exit(self, sig, frame):
        """处理退出信号"""
        logger.info("收到退出信号，正在关闭服务器...")
        self.stop()
    
    def start(self):
        """启动服务器"""
        self.running = True
        
        if self.use_http:
            self._start_http_server()
        
        self._start_stdio_server()
    
    def stop(self):
        """停止服务器"""
        self.running = False
        
        if self.http_server:
            self.http_server.shutdown()
            logger.info("HTTP服务器已关闭")
        
        logger.info("MCP服务器已停止")
    
    def _start_http_server(self):
        """启动HTTP服务器"""
        
        class MCPHTTPHandler(BaseHTTPRequestHandler):
            """处理HTTP请求的处理器"""
            
            def __init__(self, *args, **kwargs):
                self.server_ref = None
                super().__init__(*args, **kwargs)
            
            def set_server_ref(self, server):
                """设置服务器引用"""
                self.server_ref = server
            
            def log_message(self, format, *args):
                """重写日志方法，使用服务器日志"""
                logger.debug(f"{self.address_string()} - {format % args}")
            
            def do_POST(self):
                """处理POST请求"""
                try:
                    content_length = int(self.headers.get('Content-Length', 0))
                    request_body = self.rfile.read(content_length).decode('utf-8')
                    request = json.loads(request_body)
                    
                    response = self.server_ref._process_request(request)
                    
                    self.send_response(200)
                    self.send_header('Content-Type', 'application/json')
                    self.end_headers()
                    self.wfile.write(json.dumps(response).encode('utf-8'))
                
                except Exception as e:
                    logger.error(f"处理HTTP请求时出错: {e}")
                    self.send_response(500)
                    self.send_header('Content-Type', 'application/json')
                    self.end_headers()
                    self.wfile.write(json.dumps({
                        "error": str(e),
                        "status": "error"
                    }).encode('utf-8'))
            
            def do_OPTIONS(self):
                """处理OPTIONS请求，支持CORS"""
                self.send_response(200)
                self.send_header('Access-Control-Allow-Origin', '*')
                self.send_header('Access-Control-Allow-Methods', 'POST, OPTIONS')
                self.send_header('Access-Control-Allow-Headers', 'Content-Type')
                self.end_headers()
        
        # 创建HTTPHandler类的子类，设置服务器引用
        handler = type('MCPHTTPHandlerWithServer', (MCPHTTPHandler,), {'server_ref': self})
        
        # 创建并启动HTTP服务器
        self.http_server = HTTPServer(('localhost', self.http_port), handler)
        
        # 在单独的线程中运行HTTP服务器
        http_thread = threading.Thread(target=self.http_server.serve_forever)
        http_thread.daemon = True
        http_thread.start()
        
        logger.info(f"HTTP服务器已启动，监听端口 {self.http_port}")
    
    def _start_stdio_server(self):
        """启动STDIO服务器"""
        logger.info("STDIO服务器已启动，等待输入...")
        
        while self.running:
            try:
                # 从标准输入读取请求
                line = sys.stdin.readline()
                if not line:
                    # 标准输入已关闭
                    logger.info("标准输入已关闭，退出服务器")
                    self.stop()
                    break
                
                # 解析请求
                try:
                    request = json.loads(line)
                    
                    # 处理请求
                    response = self._process_request(request)
                    
                    # 发送响应
                    sys.stdout.write(json.dumps(response) + "\n")
                    sys.stdout.flush()
                
                except json.JSONDecodeError:
                    # 无效的JSON
                    error_response = {
                        "error": "Invalid JSON",
                        "status": "error"
                    }
                    sys.stdout.write(json.dumps(error_response) + "\n")
                    sys.stdout.flush()
                
            except KeyboardInterrupt:
                # 用户中断
                logger.info("用户中断，退出服务器")
                self.stop()
                break
            
            except Exception as e:
                # 其他错误
                logger.error(f"处理STDIO请求时出错: {e}")
                error_response = {
                    "error": str(e),
                    "status": "error"
                }
                sys.stdout.write(json.dumps(error_response) + "\n")
                sys.stdout.flush()
    
    def _process_request(self, request: Dict[str, Any]) -> Dict[str, Any]:
        """
        处理MCP请求
        
        Args:
            request: MCP请求字典
            
        Returns:
            MCP响应字典
        """
        # 验证请求格式
        if not isinstance(request, dict):
            return {
                "error": "Request must be a JSON object",
                "status": "error"
            }
        
        # 提取协议信息
        protocol_info = request.get("protocol", {})
        protocol_name = protocol_info.get("name")
        
        # 检查协议是否注册
        if not protocol_name or protocol_name not in self.protocols:
            return {
                "error": f"Unknown protocol: {protocol_name}",
                "status": "error"
            }
        
        # 获取协议实例
        protocol = self.protocols[protocol_name]
        
        # 提取工具信息
        tool_info = request.get("tool", {})
        tool_name = tool_info.get("name")
        tool_params = tool_info.get("parameters", {})
        
        # 检查工具是否存在
        if not tool_name or tool_name not in protocol.tools:
            return {
                "error": f"Unknown tool: {tool_name}",
                "status": "error"
            }
        
        # 执行工具
        try:
            result = protocol.execute_tool(tool_name, **tool_params)
            
            # 格式化响应
            response = protocol.format_mcp_response(
                request=request,
                result=result.get("data", result),
                status="success" if result.get("status") != "error" else "error",
                error=result.get("error")
            )
            
            return response
        
        except Exception as e:
            logger.error(f"执行工具时出错: {e}")
            
            # 格式化错误响应
            error_response = protocol.format_mcp_response(
                request=request,
                result=None,
                status="error",
                error=str(e)
            )
            
            return error_response


def main():
    """主函数"""
    import argparse
    
    parser = argparse.ArgumentParser(description="MCP协议服务器")
    parser.add_argument("--http", action="store_true", help="启用HTTP服务器")
    parser.add_argument("--port", type=int, default=8000, help="HTTP服务器端口")
    parser.add_argument("--debug", action="store_true", help="启用调试日志")
    
    args = parser.parse_args()
    
    # 设置日志级别
    if args.debug:
        logger.setLevel(logging.DEBUG)
    
    # 创建并启动服务器
    server = MCPServer(use_http=args.http, http_port=args.port)
    
    try:
        server.start()
    except KeyboardInterrupt:
        server.stop()
    except Exception as e:
        logger.error(f"服务器运行时出错: {e}")
        server.stop()


if __name__ == "__main__":
    main() 