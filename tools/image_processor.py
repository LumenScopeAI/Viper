"""
图像处理工具 - 提供图像识别、分析和转换功能
"""

import os
import io
import base64
from typing import Dict, List, Optional, Tuple, Union, Any
from PIL import Image, ImageOps, ImageEnhance, ImageFilter


class ImageProcessor:
    """
    图像处理工具类，提供图像处理、识别和分析功能
    
    该类提供以下功能:
    1. 图像基本处理（调整大小、裁剪、旋转等）
    2. 图像增强（亮度、对比度、锐化等）
    3. 图像格式转换
    4. 图像编码和解码（Base64）
    """
    
    def __init__(self):
        """初始化ImageProcessor"""
        pass
    
    def load_image(self, image_path: str) -> Optional[Image.Image]:
        """
        加载图像文件
        
        Args:
            image_path: 图像文件路径
            
        Returns:
            PIL.Image对象，如果加载失败则返回None
        """
        try:
            if not os.path.exists(image_path):
                print(f"图像文件不存在: {image_path}")
                return None
                
            image = Image.open(image_path)
            return image
        except Exception as e:
            print(f"加载图像失败: {e}")
            return None
    
    def load_image_from_bytes(self, image_bytes: bytes) -> Optional[Image.Image]:
        """
        从字节数据加载图像
        
        Args:
            image_bytes: 图像字节数据
            
        Returns:
            PIL.Image对象，如果加载失败则返回None
        """
        try:
            image = Image.open(io.BytesIO(image_bytes))
            return image
        except Exception as e:
            print(f"从字节数据加载图像失败: {e}")
            return None
    
    def load_image_from_base64(self, base64_str: str) -> Optional[Image.Image]:
        """
        从Base64字符串加载图像
        
        Args:
            base64_str: Base64编码的图像数据
            
        Returns:
            PIL.Image对象，如果加载失败则返回None
        """
        try:
            # 移除可能的头部信息，如"data:image/jpeg;base64,"
            if ',' in base64_str:
                base64_str = base64_str.split(',', 1)[1]
                
            image_bytes = base64.b64decode(base64_str)
            return self.load_image_from_bytes(image_bytes)
        except Exception as e:
            print(f"从Base64加载图像失败: {e}")
            return None
    
    def save_image(self, image: Image.Image, output_path: str, format: str = None) -> bool:
        """
        保存图像到文件
        
        Args:
            image: PIL.Image对象
            output_path: 输出文件路径
            format: 图像格式，如"JPEG"，"PNG"等，默认根据文件扩展名决定
            
        Returns:
            是否保存成功
        """
        try:
            image.save(output_path, format=format)
            return True
        except Exception as e:
            print(f"保存图像失败: {e}")
            return False
    
    def to_base64(self, image: Image.Image, format: str = "JPEG") -> Optional[str]:
        """
        将图像转换为Base64字符串
        
        Args:
            image: PIL.Image对象
            format: 图像格式，默认为"JPEG"
            
        Returns:
            Base64编码的字符串，如果转换失败则返回None
        """
        try:
            buffered = io.BytesIO()
            image.save(buffered, format=format)
            img_str = base64.b64encode(buffered.getvalue()).decode()
            return img_str
        except Exception as e:
            print(f"转换图像为Base64失败: {e}")
            return None
    
    def resize(self, image: Image.Image, width: int, height: int) -> Image.Image:
        """
        调整图像大小
        
        Args:
            image: PIL.Image对象
            width: 目标宽度
            height: 目标高度
            
        Returns:
            调整大小后的图像
        """
        return image.resize((width, height), Image.LANCZOS)
    
    def crop(self, image: Image.Image, left: int, top: int, right: int, bottom: int) -> Image.Image:
        """
        裁剪图像
        
        Args:
            image: PIL.Image对象
            left: 左边界
            top: 上边界
            right: 右边界
            bottom: 下边界
            
        Returns:
            裁剪后的图像
        """
        return image.crop((left, top, right, bottom))
    
    def rotate(self, image: Image.Image, angle: float, expand: bool = False) -> Image.Image:
        """
        旋转图像
        
        Args:
            image: PIL.Image对象
            angle: 旋转角度（度）
            expand: 是否扩展图像以完全包含旋转后的图像
            
        Returns:
            旋转后的图像
        """
        return image.rotate(angle, expand=expand)
    
    def adjust_brightness(self, image: Image.Image, factor: float) -> Image.Image:
        """
        调整图像亮度
        
        Args:
            image: PIL.Image对象
            factor: 亮度因子，值大于1增加亮度，小于1降低亮度
            
        Returns:
            调整亮度后的图像
        """
        enhancer = ImageEnhance.Brightness(image)
        return enhancer.enhance(factor)
    
    def adjust_contrast(self, image: Image.Image, factor: float) -> Image.Image:
        """
        调整图像对比度
        
        Args:
            image: PIL.Image对象
            factor: 对比度因子，值大于1增加对比度，小于1降低对比度
            
        Returns:
            调整对比度后的图像
        """
        enhancer = ImageEnhance.Contrast(image)
        return enhancer.enhance(factor)
    
    def sharpen(self, image: Image.Image, factor: float = 2.0) -> Image.Image:
        """
        锐化图像
        
        Args:
            image: PIL.Image对象
            factor: 锐化因子，值越大锐化效果越明显
            
        Returns:
            锐化后的图像
        """
        enhancer = ImageEnhance.Sharpness(image)
        return enhancer.enhance(factor)
    
    def convert_to_grayscale(self, image: Image.Image) -> Image.Image:
        """
        将图像转换为灰度
        
        Args:
            image: PIL.Image对象
            
        Returns:
            灰度图像
        """
        return image.convert('L')
    
    def apply_filter(self, image: Image.Image, filter_type: str) -> Image.Image:
        """
        应用滤镜
        
        Args:
            image: PIL.Image对象
            filter_type: 滤镜类型，如"BLUR"，"CONTOUR"，"EMBOSS"，"SHARPEN"等
            
        Returns:
            应用滤镜后的图像
        """
        filter_map = {
            "BLUR": ImageFilter.BLUR,
            "CONTOUR": ImageFilter.CONTOUR,
            "EMBOSS": ImageFilter.EMBOSS,
            "SHARPEN": ImageFilter.SHARPEN,
            "SMOOTH": ImageFilter.SMOOTH,
            "EDGE_ENHANCE": ImageFilter.EDGE_ENHANCE
        }
        
        if filter_type.upper() in filter_map:
            return image.filter(filter_map[filter_type.upper()])
        else:
            print(f"未知的滤镜类型: {filter_type}")
            return image
    
    def get_image_info(self, image: Image.Image) -> Dict[str, Any]:
        """
        获取图像信息
        
        Args:
            image: PIL.Image对象
            
        Returns:
            包含图像信息的字典
        """
        return {
            "format": image.format,
            "mode": image.mode,
            "size": {
                "width": image.width,
                "height": image.height
            }
        } 