"""
图像协议 - 提供图像处理功能的MCP协议实现
"""

import base64
import os
from PIL import Image
from io import BytesIO
from typing import Dict, List, Optional, Union, Any

from protocols.base_protocol import BaseProtocol
from tools.image_processor import ImageProcessor


class ImageProtocol(BaseProtocol):
    """
    图像协议类，遵循MCP协议规范，封装ImageProcessor工具
    
    提供以下功能:
    1. 图像加载和保存
    2. 图像处理和转换
    3. 图像信息获取
    """
    
    def __init__(self):
        """初始化ImageProtocol"""
        super().__init__(
            name="ImageProtocol",
            version="1.0.0",
            description="提供图像处理功能的MCP协议"
        )
        
        # 初始化ImageProcessor工具
        self.processor = ImageProcessor()
        
        # 注册工具
        self._register_tools()
    
    def _register_tools(self):
        """注册协议提供的工具"""
        
        # 加载图像工具
        self.register_tool(
            name="load_image",
            func=self._load_image,
            description="加载图像文件",
            parameters={
                "type": "object",
                "properties": {
                    "image_path": {"type": "string", "description": "图像文件路径"}
                },
                "required": ["image_path"]
            },
            returns={
                "type": "object",
                "properties": {
                    "image_id": {"type": "string", "description": "图像资源ID"},
                    "width": {"type": "integer", "description": "图像宽度"},
                    "height": {"type": "integer", "description": "图像高度"},
                    "format": {"type": "string", "description": "图像格式"},
                    "mode": {"type": "string", "description": "图像模式"}
                }
            }
        )
        
        # 从Base64加载图像工具
        self.register_tool(
            name="load_image_from_base64",
            func=self._load_image_from_base64,
            description="从Base64字符串加载图像",
            parameters={
                "type": "object",
                "properties": {
                    "base64_str": {"type": "string", "description": "Base64编码的图像数据"}
                },
                "required": ["base64_str"]
            },
            returns={
                "type": "object",
                "properties": {
                    "image_id": {"type": "string", "description": "图像资源ID"},
                    "width": {"type": "integer", "description": "图像宽度"},
                    "height": {"type": "integer", "description": "图像高度"},
                    "format": {"type": "string", "description": "图像格式"},
                    "mode": {"type": "string", "description": "图像模式"}
                }
            }
        )
        
        # 保存图像工具
        self.register_tool(
            name="save_image",
            func=self._save_image,
            description="保存图像到文件",
            parameters={
                "type": "object",
                "properties": {
                    "image_id": {"type": "string", "description": "图像资源ID"},
                    "output_path": {"type": "string", "description": "输出文件路径"},
                    "format": {"type": "string", "description": "图像格式", "optional": True}
                },
                "required": ["image_id", "output_path"]
            },
            returns={
                "type": "object",
                "properties": {
                    "success": {"type": "boolean", "description": "是否保存成功"},
                    "path": {"type": "string", "description": "保存的文件路径"}
                }
            }
        )
        
        # 转换为Base64工具
        self.register_tool(
            name="to_base64",
            func=self._to_base64,
            description="将图像转换为Base64字符串",
            parameters={
                "type": "object",
                "properties": {
                    "image_id": {"type": "string", "description": "图像资源ID"},
                    "format": {"type": "string", "description": "图像格式", "optional": True}
                },
                "required": ["image_id"]
            },
            returns={
                "type": "object",
                "properties": {
                    "base64_str": {"type": "string", "description": "Base64编码的图像数据"}
                }
            }
        )
        
        # 调整图像大小工具
        self.register_tool(
            name="resize",
            func=self._resize,
            description="调整图像大小",
            parameters={
                "type": "object",
                "properties": {
                    "image_id": {"type": "string", "description": "图像资源ID"},
                    "width": {"type": "integer", "description": "目标宽度"},
                    "height": {"type": "integer", "description": "目标高度"}
                },
                "required": ["image_id", "width", "height"]
            },
            returns={
                "type": "object",
                "properties": {
                    "image_id": {"type": "string", "description": "处理后的图像资源ID"},
                    "width": {"type": "integer", "description": "图像宽度"},
                    "height": {"type": "integer", "description": "图像高度"}
                }
            }
        )
        
        # 裁剪图像工具
        self.register_tool(
            name="crop",
            func=self._crop,
            description="裁剪图像",
            parameters={
                "type": "object",
                "properties": {
                    "image_id": {"type": "string", "description": "图像资源ID"},
                    "left": {"type": "integer", "description": "左边界"},
                    "top": {"type": "integer", "description": "上边界"},
                    "right": {"type": "integer", "description": "右边界"},
                    "bottom": {"type": "integer", "description": "下边界"}
                },
                "required": ["image_id", "left", "top", "right", "bottom"]
            },
            returns={
                "type": "object",
                "properties": {
                    "image_id": {"type": "string", "description": "处理后的图像资源ID"},
                    "width": {"type": "integer", "description": "图像宽度"},
                    "height": {"type": "integer", "description": "图像高度"}
                }
            }
        )
        
        # 旋转图像工具
        self.register_tool(
            name="rotate",
            func=self._rotate,
            description="旋转图像",
            parameters={
                "type": "object",
                "properties": {
                    "image_id": {"type": "string", "description": "图像资源ID"},
                    "angle": {"type": "number", "description": "旋转角度（度）"},
                    "expand": {"type": "boolean", "description": "是否扩展图像", "optional": True}
                },
                "required": ["image_id", "angle"]
            },
            returns={
                "type": "object",
                "properties": {
                    "image_id": {"type": "string", "description": "处理后的图像资源ID"},
                    "width": {"type": "integer", "description": "图像宽度"},
                    "height": {"type": "integer", "description": "图像高度"}
                }
            }
        )
        
        # 调整图像亮度工具
        self.register_tool(
            name="adjust_brightness",
            func=self._adjust_brightness,
            description="调整图像亮度",
            parameters={
                "type": "object",
                "properties": {
                    "image_id": {"type": "string", "description": "图像资源ID"},
                    "factor": {"type": "number", "description": "亮度因子"}
                },
                "required": ["image_id", "factor"]
            },
            returns={
                "type": "object",
                "properties": {
                    "image_id": {"type": "string", "description": "处理后的图像资源ID"}
                }
            }
        )
        
        # 调整图像对比度工具
        self.register_tool(
            name="adjust_contrast",
            func=self._adjust_contrast,
            description="调整图像对比度",
            parameters={
                "type": "object",
                "properties": {
                    "image_id": {"type": "string", "description": "图像资源ID"},
                    "factor": {"type": "number", "description": "对比度因子"}
                },
                "required": ["image_id", "factor"]
            },
            returns={
                "type": "object",
                "properties": {
                    "image_id": {"type": "string", "description": "处理后的图像资源ID"}
                }
            }
        )
        
        # 锐化图像工具
        self.register_tool(
            name="sharpen",
            func=self._sharpen,
            description="锐化图像",
            parameters={
                "type": "object",
                "properties": {
                    "image_id": {"type": "string", "description": "图像资源ID"},
                    "factor": {"type": "number", "description": "锐化因子", "optional": True}
                },
                "required": ["image_id"]
            },
            returns={
                "type": "object",
                "properties": {
                    "image_id": {"type": "string", "description": "处理后的图像资源ID"}
                }
            }
        )
        
        # 转换为灰度图像工具
        self.register_tool(
            name="convert_to_grayscale",
            func=self._convert_to_grayscale,
            description="将图像转换为灰度",
            parameters={
                "type": "object",
                "properties": {
                    "image_id": {"type": "string", "description": "图像资源ID"}
                },
                "required": ["image_id"]
            },
            returns={
                "type": "object",
                "properties": {
                    "image_id": {"type": "string", "description": "处理后的图像资源ID"}
                }
            }
        )
        
        # 应用滤镜工具
        self.register_tool(
            name="apply_filter",
            func=self._apply_filter,
            description="应用滤镜",
            parameters={
                "type": "object",
                "properties": {
                    "image_id": {"type": "string", "description": "图像资源ID"},
                    "filter_type": {
                        "type": "string", 
                        "description": "滤镜类型",
                        "enum": ["BLUR", "CONTOUR", "EMBOSS", "SHARPEN", "SMOOTH", "EDGE_ENHANCE"]
                    }
                },
                "required": ["image_id", "filter_type"]
            },
            returns={
                "type": "object",
                "properties": {
                    "image_id": {"type": "string", "description": "处理后的图像资源ID"}
                }
            }
        )
        
        # 获取图像信息工具
        self.register_tool(
            name="get_image_info",
            func=self._get_image_info,
            description="获取图像信息",
            parameters={
                "type": "object",
                "properties": {
                    "image_id": {"type": "string", "description": "图像资源ID"}
                },
                "required": ["image_id"]
            },
            returns={
                "type": "object",
                "properties": {
                    "format": {"type": "string", "description": "图像格式"},
                    "mode": {"type": "string", "description": "图像模式"},
                    "size": {
                        "type": "object",
                        "properties": {
                            "width": {"type": "integer", "description": "图像宽度"},
                            "height": {"type": "integer", "description": "图像高度"}
                        }
                    }
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
    
    def _load_image(self, image_path: str) -> Dict[str, Any]:
        """
        加载图像文件
        
        Args:
            image_path: 图像文件路径
            
        Returns:
            包含图像信息的字典
        """
        image = self.processor.load_image(image_path)
        if image:
            resource_id = self.register_resource(
                name=os.path.basename(image_path),
                resource_type="image",
                data=image,
                description=f"Image loaded from {image_path}"
            )
            
            return {
                "image_id": resource_id,
                "width": image.width,
                "height": image.height,
                "format": image.format if image.format else "unknown",
                "mode": image.mode
            }
        else:
            return {
                "error": f"Failed to load image from {image_path}"
            }
    
    def _load_image_from_base64(self, base64_str: str) -> Dict[str, Any]:
        """
        从Base64字符串加载图像
        
        Args:
            base64_str: Base64编码的图像数据
            
        Returns:
            包含图像信息的字典
        """
        image = self.processor.load_image_from_base64(base64_str)
        if image:
            resource_id = self.register_resource(
                name="base64_image",
                resource_type="image",
                data=image,
                description="Image loaded from Base64 string"
            )
            
            return {
                "image_id": resource_id,
                "width": image.width,
                "height": image.height,
                "format": image.format if image.format else "unknown",
                "mode": image.mode
            }
        else:
            return {
                "error": "Failed to load image from Base64 string"
            }
    
    def _save_image(self, image_id: str, output_path: str, format: str = None) -> Dict[str, Any]:
        """
        保存图像到文件
        
        Args:
            image_id: 图像资源ID
            output_path: 输出文件路径
            format: 图像格式
            
        Returns:
            包含保存结果的字典
        """
        resource = self.get_resource(image_id)
        if not resource:
            return {"success": False, "error": f"Image with ID {image_id} not found"}
        
        image = resource["data"]
        success = self.processor.save_image(image, output_path, format)
        
        return {
            "success": success,
            "path": output_path if success else None
        }
    
    def _to_base64(self, image_id: str, format: str = "JPEG") -> Dict[str, str]:
        """
        将图像转换为Base64字符串
        
        Args:
            image_id: 图像资源ID
            format: 图像格式
            
        Returns:
            包含Base64编码字符串的字典
        """
        resource = self.get_resource(image_id)
        if not resource:
            return {"error": f"Image with ID {image_id} not found"}
        
        image = resource["data"]
        base64_str = self.processor.to_base64(image, format)
        
        return {
            "base64_str": base64_str if base64_str else ""
        }
    
    def _resize(self, image_id: str, width: int, height: int) -> Dict[str, Any]:
        """
        调整图像大小
        
        Args:
            image_id: 图像资源ID
            width: 目标宽度
            height: 目标高度
            
        Returns:
            包含处理后图像信息的字典
        """
        resource = self.get_resource(image_id)
        if not resource:
            return {"error": f"Image with ID {image_id} not found"}
        
        image = resource["data"]
        resized_image = self.processor.resize(image, width, height)
        
        new_resource_id = self.register_resource(
            name=f"{resource['name']}_resized",
            resource_type="image",
            data=resized_image,
            description=f"Resized image from {image_id}"
        )
        
        return {
            "image_id": new_resource_id,
            "width": resized_image.width,
            "height": resized_image.height
        }
    
    def _crop(self, image_id: str, left: int, top: int, right: int, bottom: int) -> Dict[str, Any]:
        """
        裁剪图像
        
        Args:
            image_id: 图像资源ID
            left: 左边界
            top: 上边界
            right: 右边界
            bottom: 下边界
            
        Returns:
            包含处理后图像信息的字典
        """
        resource = self.get_resource(image_id)
        if not resource:
            return {"error": f"Image with ID {image_id} not found"}
        
        image = resource["data"]
        cropped_image = self.processor.crop(image, left, top, right, bottom)
        
        new_resource_id = self.register_resource(
            name=f"{resource['name']}_cropped",
            resource_type="image",
            data=cropped_image,
            description=f"Cropped image from {image_id}"
        )
        
        return {
            "image_id": new_resource_id,
            "width": cropped_image.width,
            "height": cropped_image.height
        }
    
    def _rotate(self, image_id: str, angle: float, expand: bool = False) -> Dict[str, Any]:
        """
        旋转图像
        
        Args:
            image_id: 图像资源ID
            angle: 旋转角度（度）
            expand: 是否扩展图像
            
        Returns:
            包含处理后图像信息的字典
        """
        resource = self.get_resource(image_id)
        if not resource:
            return {"error": f"Image with ID {image_id} not found"}
        
        image = resource["data"]
        rotated_image = self.processor.rotate(image, angle, expand)
        
        new_resource_id = self.register_resource(
            name=f"{resource['name']}_rotated",
            resource_type="image",
            data=rotated_image,
            description=f"Rotated image from {image_id}"
        )
        
        return {
            "image_id": new_resource_id,
            "width": rotated_image.width,
            "height": rotated_image.height
        }
    
    def _adjust_brightness(self, image_id: str, factor: float) -> Dict[str, str]:
        """
        调整图像亮度
        
        Args:
            image_id: 图像资源ID
            factor: 亮度因子
            
        Returns:
            包含处理后图像ID的字典
        """
        resource = self.get_resource(image_id)
        if not resource:
            return {"error": f"Image with ID {image_id} not found"}
        
        image = resource["data"]
        adjusted_image = self.processor.adjust_brightness(image, factor)
        
        new_resource_id = self.register_resource(
            name=f"{resource['name']}_brightness",
            resource_type="image",
            data=adjusted_image,
            description=f"Brightness adjusted image from {image_id}"
        )
        
        return {
            "image_id": new_resource_id
        }
    
    def _adjust_contrast(self, image_id: str, factor: float) -> Dict[str, str]:
        """
        调整图像对比度
        
        Args:
            image_id: 图像资源ID
            factor: 对比度因子
            
        Returns:
            包含处理后图像ID的字典
        """
        resource = self.get_resource(image_id)
        if not resource:
            return {"error": f"Image with ID {image_id} not found"}
        
        image = resource["data"]
        adjusted_image = self.processor.adjust_contrast(image, factor)
        
        new_resource_id = self.register_resource(
            name=f"{resource['name']}_contrast",
            resource_type="image",
            data=adjusted_image,
            description=f"Contrast adjusted image from {image_id}"
        )
        
        return {
            "image_id": new_resource_id
        }
    
    def _sharpen(self, image_id: str, factor: float = 2.0) -> Dict[str, str]:
        """
        锐化图像
        
        Args:
            image_id: 图像资源ID
            factor: 锐化因子
            
        Returns:
            包含处理后图像ID的字典
        """
        resource = self.get_resource(image_id)
        if not resource:
            return {"error": f"Image with ID {image_id} not found"}
        
        image = resource["data"]
        sharpened_image = self.processor.sharpen(image, factor)
        
        new_resource_id = self.register_resource(
            name=f"{resource['name']}_sharpened",
            resource_type="image",
            data=sharpened_image,
            description=f"Sharpened image from {image_id}"
        )
        
        return {
            "image_id": new_resource_id
        }
    
    def _convert_to_grayscale(self, image_id: str) -> Dict[str, str]:
        """
        将图像转换为灰度
        
        Args:
            image_id: 图像资源ID
            
        Returns:
            包含处理后图像ID的字典
        """
        resource = self.get_resource(image_id)
        if not resource:
            return {"error": f"Image with ID {image_id} not found"}
        
        image = resource["data"]
        grayscale_image = self.processor.convert_to_grayscale(image)
        
        new_resource_id = self.register_resource(
            name=f"{resource['name']}_grayscale",
            resource_type="image",
            data=grayscale_image,
            description=f"Grayscale image from {image_id}"
        )
        
        return {
            "image_id": new_resource_id
        }
    
    def _apply_filter(self, image_id: str, filter_type: str) -> Dict[str, str]:
        """
        应用滤镜
        
        Args:
            image_id: 图像资源ID
            filter_type: 滤镜类型
            
        Returns:
            包含处理后图像ID的字典
        """
        resource = self.get_resource(image_id)
        if not resource:
            return {"error": f"Image with ID {image_id} not found"}
        
        image = resource["data"]
        filtered_image = self.processor.apply_filter(image, filter_type)
        
        new_resource_id = self.register_resource(
            name=f"{resource['name']}_{filter_type.lower()}",
            resource_type="image",
            data=filtered_image,
            description=f"Filtered image from {image_id} with {filter_type}"
        )
        
        return {
            "image_id": new_resource_id
        }
    
    def _get_image_info(self, image_id: str) -> Dict[str, Any]:
        """
        获取图像信息
        
        Args:
            image_id: 图像资源ID
            
        Returns:
            包含图像信息的字典
        """
        resource = self.get_resource(image_id)
        if not resource:
            return {"error": f"Image with ID {image_id} not found"}
        
        image = resource["data"]
        info = self.processor.get_image_info(image)
        
        return info 