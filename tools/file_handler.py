"""
文件处理工具 - 提供文件读写和管理功能
"""

import os
import shutil
import json
import csv
import yaml
import xml.etree.ElementTree as ET
from typing import Dict, List, Optional, Union, Any, BinaryIO, TextIO


class FileHandler:
    """
    文件处理工具类，提供文件读写和管理功能
    
    该类提供以下功能:
    1. 基本文件操作（读、写、复制、移动、删除等）
    2. 特定格式文件处理（JSON、CSV、YAML、XML等）
    3. 文件信息获取
    4. 目录操作
    """
    
    def __init__(self):
        """初始化FileHandler"""
        pass
    
    # 基本文件操作
    
    def read_text(self, file_path: str, encoding: str = 'utf-8') -> Optional[str]:
        """
        读取文本文件
        
        Args:
            file_path: 文件路径
            encoding: 文件编码，默认为utf-8
            
        Returns:
            文件内容，如果读取失败则返回None
        """
        try:
            with open(file_path, 'r', encoding=encoding) as f:
                return f.read()
        except Exception as e:
            print(f"读取文本文件失败: {e}")
            return None
    
    def read_binary(self, file_path: str) -> Optional[bytes]:
        """
        读取二进制文件
        
        Args:
            file_path: 文件路径
            
        Returns:
            文件内容，如果读取失败则返回None
        """
        try:
            with open(file_path, 'rb') as f:
                return f.read()
        except Exception as e:
            print(f"读取二进制文件失败: {e}")
            return None
    
    def write_text(self, file_path: str, content: str, encoding: str = 'utf-8') -> bool:
        """
        写入文本文件
        
        Args:
            file_path: 文件路径
            content: 要写入的内容
            encoding: 文件编码，默认为utf-8
            
        Returns:
            是否写入成功
        """
        try:
            with open(file_path, 'w', encoding=encoding) as f:
                f.write(content)
            return True
        except Exception as e:
            print(f"写入文本文件失败: {e}")
            return False
    
    def write_binary(self, file_path: str, content: bytes) -> bool:
        """
        写入二进制文件
        
        Args:
            file_path: 文件路径
            content: 要写入的内容
            
        Returns:
            是否写入成功
        """
        try:
            with open(file_path, 'wb') as f:
                f.write(content)
            return True
        except Exception as e:
            print(f"写入二进制文件失败: {e}")
            return False
    
    def append_text(self, file_path: str, content: str, encoding: str = 'utf-8') -> bool:
        """
        追加内容到文本文件
        
        Args:
            file_path: 文件路径
            content: 要追加的内容
            encoding: 文件编码，默认为utf-8
            
        Returns:
            是否追加成功
        """
        try:
            with open(file_path, 'a', encoding=encoding) as f:
                f.write(content)
            return True
        except Exception as e:
            print(f"追加文本文件失败: {e}")
            return False
    
    def copy_file(self, source_path: str, destination_path: str) -> bool:
        """
        复制文件
        
        Args:
            source_path: 源文件路径
            destination_path: 目标文件路径
            
        Returns:
            是否复制成功
        """
        try:
            shutil.copy2(source_path, destination_path)
            return True
        except Exception as e:
            print(f"复制文件失败: {e}")
            return False
    
    def move_file(self, source_path: str, destination_path: str) -> bool:
        """
        移动文件
        
        Args:
            source_path: 源文件路径
            destination_path: 目标文件路径
            
        Returns:
            是否移动成功
        """
        try:
            shutil.move(source_path, destination_path)
            return True
        except Exception as e:
            print(f"移动文件失败: {e}")
            return False
    
    def delete_file(self, file_path: str) -> bool:
        """
        删除文件
        
        Args:
            file_path: 文件路径
            
        Returns:
            是否删除成功
        """
        try:
            os.remove(file_path)
            return True
        except Exception as e:
            print(f"删除文件失败: {e}")
            return False
    
    # 特定格式文件处理
    
    def read_json(self, file_path: str, encoding: str = 'utf-8') -> Optional[Union[Dict, List]]:
        """
        读取JSON文件
        
        Args:
            file_path: 文件路径
            encoding: 文件编码，默认为utf-8
            
        Returns:
            JSON数据，如果读取失败则返回None
        """
        try:
            with open(file_path, 'r', encoding=encoding) as f:
                return json.load(f)
        except Exception as e:
            print(f"读取JSON文件失败: {e}")
            return None
    
    def write_json(self, file_path: str, data: Union[Dict, List], encoding: str = 'utf-8', indent: int = 4) -> bool:
        """
        写入JSON文件
        
        Args:
            file_path: 文件路径
            data: 要写入的数据
            encoding: 文件编码，默认为utf-8
            indent: 缩进空格数，默认为4
            
        Returns:
            是否写入成功
        """
        try:
            with open(file_path, 'w', encoding=encoding) as f:
                json.dump(data, f, ensure_ascii=False, indent=indent)
            return True
        except Exception as e:
            print(f"写入JSON文件失败: {e}")
            return False
    
    def read_csv(self, file_path: str, has_header: bool = True, encoding: str = 'utf-8') -> Optional[List[Dict]]:
        """
        读取CSV文件
        
        Args:
            file_path: 文件路径
            has_header: 是否有表头，默认为True
            encoding: 文件编码，默认为utf-8
            
        Returns:
            CSV数据列表，如果读取失败则返回None
        """
        try:
            rows = []
            with open(file_path, 'r', encoding=encoding, newline='') as f:
                reader = csv.reader(f)
                if has_header:
                    header = next(reader)
                    for row in reader:
                        rows.append(dict(zip(header, row)))
                else:
                    for row in reader:
                        rows.append(row)
            return rows
        except Exception as e:
            print(f"读取CSV文件失败: {e}")
            return None
    
    def write_csv(self, file_path: str, data: List[Union[Dict, List]], headers: List[str] = None, encoding: str = 'utf-8') -> bool:
        """
        写入CSV文件
        
        Args:
            file_path: 文件路径
            data: 要写入的数据
            headers: 表头列表，如果data为字典列表且headers为None，则使用第一个字典的键作为表头
            encoding: 文件编码，默认为utf-8
            
        Returns:
            是否写入成功
        """
        try:
            with open(file_path, 'w', encoding=encoding, newline='') as f:
                writer = csv.writer(f)
                
                if data and isinstance(data[0], dict):
                    if headers is None:
                        headers = list(data[0].keys())
                    writer.writerow(headers)
                    for row in data:
                        writer.writerow([row.get(key, '') for key in headers])
                else:
                    if headers:
                        writer.writerow(headers)
                    writer.writerows(data)
                
            return True
        except Exception as e:
            print(f"写入CSV文件失败: {e}")
            return False
    
    def read_yaml(self, file_path: str, encoding: str = 'utf-8') -> Optional[Union[Dict, List]]:
        """
        读取YAML文件
        
        Args:
            file_path: 文件路径
            encoding: 文件编码，默认为utf-8
            
        Returns:
            YAML数据，如果读取失败则返回None
        """
        try:
            with open(file_path, 'r', encoding=encoding) as f:
                return yaml.safe_load(f)
        except Exception as e:
            print(f"读取YAML文件失败: {e}")
            return None
    
    def write_yaml(self, file_path: str, data: Union[Dict, List], encoding: str = 'utf-8') -> bool:
        """
        写入YAML文件
        
        Args:
            file_path: 文件路径
            data: 要写入的数据
            encoding: 文件编码，默认为utf-8
            
        Returns:
            是否写入成功
        """
        try:
            with open(file_path, 'w', encoding=encoding) as f:
                yaml.dump(data, f, allow_unicode=True)
            return True
        except Exception as e:
            print(f"写入YAML文件失败: {e}")
            return False
    
    def read_xml(self, file_path: str) -> Optional[ET.Element]:
        """
        读取XML文件
        
        Args:
            file_path: 文件路径
            
        Returns:
            XML根元素，如果读取失败则返回None
        """
        try:
            tree = ET.parse(file_path)
            return tree.getroot()
        except Exception as e:
            print(f"读取XML文件失败: {e}")
            return None
    
    def write_xml(self, file_path: str, root_element: ET.Element, encoding: str = 'utf-8') -> bool:
        """
        写入XML文件
        
        Args:
            file_path: 文件路径
            root_element: XML根元素
            encoding: 文件编码，默认为utf-8
            
        Returns:
            是否写入成功
        """
        try:
            tree = ET.ElementTree(root_element)
            tree.write(file_path, encoding=encoding, xml_declaration=True)
            return True
        except Exception as e:
            print(f"写入XML文件失败: {e}")
            return False
    
    # 文件信息获取
    
    def get_file_info(self, file_path: str) -> Optional[Dict[str, Any]]:
        """
        获取文件信息
        
        Args:
            file_path: 文件路径
            
        Returns:
            文件信息字典，如果获取失败则返回None
        """
        try:
            stat = os.stat(file_path)
            return {
                "name": os.path.basename(file_path),
                "path": os.path.abspath(file_path),
                "size": stat.st_size,
                "created_time": stat.st_ctime,
                "modified_time": stat.st_mtime,
                "accessed_time": stat.st_atime,
                "is_file": os.path.isfile(file_path),
                "is_dir": os.path.isdir(file_path),
                "extension": os.path.splitext(file_path)[1]
            }
        except Exception as e:
            print(f"获取文件信息失败: {e}")
            return None
    
    def file_exists(self, file_path: str) -> bool:
        """
        检查文件是否存在
        
        Args:
            file_path: 文件路径
            
        Returns:
            文件是否存在
        """
        return os.path.exists(file_path) and os.path.isfile(file_path)
    
    # 目录操作
    
    def create_directory(self, dir_path: str) -> bool:
        """
        创建目录
        
        Args:
            dir_path: 目录路径
            
        Returns:
            是否创建成功
        """
        try:
            os.makedirs(dir_path, exist_ok=True)
            return True
        except Exception as e:
            print(f"创建目录失败: {e}")
            return False
    
    def delete_directory(self, dir_path: str, recursive: bool = False) -> bool:
        """
        删除目录
        
        Args:
            dir_path: 目录路径
            recursive: 是否递归删除，默认为False
            
        Returns:
            是否删除成功
        """
        try:
            if recursive:
                shutil.rmtree(dir_path)
            else:
                os.rmdir(dir_path)
            return True
        except Exception as e:
            print(f"删除目录失败: {e}")
            return False
    
    def list_directory(self, dir_path: str, pattern: str = "*") -> Optional[List[str]]:
        """
        列出目录内容
        
        Args:
            dir_path: 目录路径
            pattern: 文件匹配模式，默认为"*"
            
        Returns:
            目录内容列表，如果列出失败则返回None
        """
        try:
            import glob
            return glob.glob(os.path.join(dir_path, pattern))
        except Exception as e:
            print(f"列出目录内容失败: {e}")
            return None 