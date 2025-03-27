"""
数据转换工具 - 提供各种数据格式的转换功能
"""

import json
import csv
import yaml
import xml.etree.ElementTree as ET
import base64
import pickle
import io
import pandas as pd
from typing import Dict, List, Optional, Union, Any, BinaryIO, TextIO


class DataTransformer:
    """
    数据转换工具类，提供各种数据格式的转换功能
    
    该类提供以下功能:
    1. 格式转换（JSON、CSV、YAML、XML、DataFrame等之间的互相转换）
    2. 数据编码和解码（Base64、pickle等）
    3. 数据结构转换（列表、字典、数据帧等之间的转换）
    """
    
    def __init__(self):
        """初始化DataTransformer"""
        pass
    
    # JSON 转换
    
    def dict_to_json(self, data: Dict, ensure_ascii: bool = False, indent: int = 4) -> str:
        """
        字典转JSON字符串
        
        Args:
            data: 字典数据
            ensure_ascii: 是否确保ASCII编码，默认为False
            indent: 缩进空格数，默认为4
            
        Returns:
            JSON字符串
        """
        try:
            return json.dumps(data, ensure_ascii=ensure_ascii, indent=indent)
        except Exception as e:
            print(f"字典转JSON失败: {e}")
            return "{}"
    
    def json_to_dict(self, json_str: str) -> Dict:
        """
        JSON字符串转字典
        
        Args:
            json_str: JSON字符串
            
        Returns:
            字典数据，如果转换失败则返回空字典
        """
        try:
            return json.loads(json_str)
        except Exception as e:
            print(f"JSON转字典失败: {e}")
            return {}
    
    # YAML 转换
    
    def dict_to_yaml(self, data: Dict) -> str:
        """
        字典转YAML字符串
        
        Args:
            data: 字典数据
            
        Returns:
            YAML字符串
        """
        try:
            return yaml.dump(data, allow_unicode=True)
        except Exception as e:
            print(f"字典转YAML失败: {e}")
            return ""
    
    def yaml_to_dict(self, yaml_str: str) -> Dict:
        """
        YAML字符串转字典
        
        Args:
            yaml_str: YAML字符串
            
        Returns:
            字典数据，如果转换失败则返回空字典
        """
        try:
            return yaml.safe_load(yaml_str)
        except Exception as e:
            print(f"YAML转字典失败: {e}")
            return {}
    
    # XML 转换
    
    def dict_to_xml(self, data: Dict, root_name: str = "root") -> str:
        """
        字典转XML字符串
        
        Args:
            data: 字典数据
            root_name: 根元素名称，默认为"root"
            
        Returns:
            XML字符串
        """
        try:
            def _dict_to_xml_element(parent: ET.Element, data: Dict):
                for key, value in data.items():
                    if isinstance(value, dict):
                        elem = ET.SubElement(parent, key)
                        _dict_to_xml_element(elem, value)
                    elif isinstance(value, list):
                        for item in value:
                            elem = ET.SubElement(parent, key)
                            if isinstance(item, dict):
                                _dict_to_xml_element(elem, item)
                            else:
                                elem.text = str(item)
                    else:
                        elem = ET.SubElement(parent, key)
                        elem.text = str(value)
            
            root = ET.Element(root_name)
            _dict_to_xml_element(root, data)
            
            return ET.tostring(root, encoding="unicode")
        except Exception as e:
            print(f"字典转XML失败: {e}")
            return f"<{root_name}></{root_name}>"
    
    def xml_to_dict(self, xml_str: str) -> Dict:
        """
        XML字符串转字典
        
        Args:
            xml_str: XML字符串
            
        Returns:
            字典数据，如果转换失败则返回空字典
        """
        try:
            def _element_to_dict(element: ET.Element) -> Dict:
                result = {}
                for child in element:
                    child_dict = _element_to_dict(child)
                    if child.tag in result:
                        if not isinstance(result[child.tag], list):
                            result[child.tag] = [result[child.tag]]
                        result[child.tag].append(child_dict if child_dict else child.text)
                    else:
                        result[child.tag] = child_dict if child_dict else child.text
                return result
            
            root = ET.fromstring(xml_str)
            return {root.tag: _element_to_dict(root)}
        except Exception as e:
            print(f"XML转字典失败: {e}")
            return {}
    
    # CSV 转换
    
    def list_to_csv(self, data: List[Union[Dict, List]], headers: List[str] = None) -> str:
        """
        列表转CSV字符串
        
        Args:
            data: 列表数据，可以是字典列表或列表的列表
            headers: 表头列表，如果data为字典列表且headers为None，则使用第一个字典的键作为表头
            
        Returns:
            CSV字符串
        """
        try:
            output = io.StringIO()
            writer = csv.writer(output)
            
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
            
            return output.getvalue()
        except Exception as e:
            print(f"列表转CSV失败: {e}")
            return ""
    
    def csv_to_list(self, csv_str: str, has_header: bool = True) -> List:
        """
        CSV字符串转列表
        
        Args:
            csv_str: CSV字符串
            has_header: 是否有表头，默认为True
            
        Returns:
            列表数据，如果转换失败则返回空列表
        """
        try:
            input_file = io.StringIO(csv_str)
            reader = csv.reader(input_file)
            rows = []
            
            if has_header:
                header = next(reader)
                for row in reader:
                    rows.append(dict(zip(header, row)))
            else:
                rows = [row for row in reader]
            
            return rows
        except Exception as e:
            print(f"CSV转列表失败: {e}")
            return []
    
    # DataFrame 转换
    
    def dict_to_dataframe(self, data: Dict) -> pd.DataFrame:
        """
        字典转DataFrame
        
        Args:
            data: 字典数据
            
        Returns:
            DataFrame
        """
        try:
            return pd.DataFrame.from_dict(data)
        except Exception as e:
            print(f"字典转DataFrame失败: {e}")
            return pd.DataFrame()
    
    def list_to_dataframe(self, data: List[Dict]) -> pd.DataFrame:
        """
        列表转DataFrame
        
        Args:
            data: 字典列表
            
        Returns:
            DataFrame
        """
        try:
            return pd.DataFrame(data)
        except Exception as e:
            print(f"列表转DataFrame失败: {e}")
            return pd.DataFrame()
    
    def dataframe_to_dict(self, df: pd.DataFrame, orient: str = "records") -> Dict:
        """
        DataFrame转字典
        
        Args:
            df: DataFrame
            orient: 转换方向，可选值为"dict"，"list"，"series"，"split"，"records"，"index"，默认为"records"
            
        Returns:
            字典数据
        """
        try:
            return df.to_dict(orient=orient)
        except Exception as e:
            print(f"DataFrame转字典失败: {e}")
            return {}
    
    def dataframe_to_list(self, df: pd.DataFrame) -> List[Dict]:
        """
        DataFrame转列表
        
        Args:
            df: DataFrame
            
        Returns:
            字典列表
        """
        try:
            return df.to_dict(orient="records")
        except Exception as e:
            print(f"DataFrame转列表失败: {e}")
            return []
    
    def dataframe_to_csv(self, df: pd.DataFrame) -> str:
        """
        DataFrame转CSV字符串
        
        Args:
            df: DataFrame
            
        Returns:
            CSV字符串
        """
        try:
            return df.to_csv(index=False)
        except Exception as e:
            print(f"DataFrame转CSV失败: {e}")
            return ""
    
    def csv_to_dataframe(self, csv_str: str) -> pd.DataFrame:
        """
        CSV字符串转DataFrame
        
        Args:
            csv_str: CSV字符串
            
        Returns:
            DataFrame
        """
        try:
            return pd.read_csv(io.StringIO(csv_str))
        except Exception as e:
            print(f"CSV转DataFrame失败: {e}")
            return pd.DataFrame()
    
    def dataframe_to_json(self, df: pd.DataFrame, orient: str = "records") -> str:
        """
        DataFrame转JSON字符串
        
        Args:
            df: DataFrame
            orient: 转换方向，可选值为"dict"，"list"，"series"，"split"，"records"，"index"，默认为"records"
            
        Returns:
            JSON字符串
        """
        try:
            return df.to_json(orient=orient, force_ascii=False)
        except Exception as e:
            print(f"DataFrame转JSON失败: {e}")
            return "[]"
    
    def json_to_dataframe(self, json_str: str, orient: str = "records") -> pd.DataFrame:
        """
        JSON字符串转DataFrame
        
        Args:
            json_str: JSON字符串
            orient: 转换方向，可选值为"dict"，"list"，"series"，"split"，"records"，"index"，默认为"records"
            
        Returns:
            DataFrame
        """
        try:
            return pd.read_json(json_str, orient=orient)
        except Exception as e:
            print(f"JSON转DataFrame失败: {e}")
            return pd.DataFrame()
    
    # 编码和解码
    
    def to_base64(self, data: Union[str, bytes]) -> str:
        """
        将数据转换为Base64编码
        
        Args:
            data: 要编码的数据，可以是字符串或字节
            
        Returns:
            Base64编码的字符串
        """
        try:
            if isinstance(data, str):
                data = data.encode('utf-8')
            return base64.b64encode(data).decode('utf-8')
        except Exception as e:
            print(f"转换为Base64失败: {e}")
            return ""
    
    def from_base64(self, base64_str: str, as_bytes: bool = False) -> Union[str, bytes]:
        """
        从Base64编码中解码数据
        
        Args:
            base64_str: Base64编码的字符串
            as_bytes: 是否返回字节类型，默认为False（返回字符串）
            
        Returns:
            解码后的数据，默认为字符串，如果as_bytes为True则为字节
        """
        try:
            decoded = base64.b64decode(base64_str)
            if as_bytes:
                return decoded
            else:
                return decoded.decode('utf-8')
        except Exception as e:
            print(f"从Base64解码失败: {e}")
            return b"" if as_bytes else ""
    
    def to_pickle(self, data: Any) -> bytes:
        """
        将数据序列化为Pickle格式
        
        Args:
            data: 要序列化的数据
            
        Returns:
            序列化后的字节数据
        """
        try:
            return pickle.dumps(data)
        except Exception as e:
            print(f"序列化为Pickle失败: {e}")
            return b""
    
    def from_pickle(self, pickle_bytes: bytes) -> Any:
        """
        从Pickle格式反序列化数据
        
        Args:
            pickle_bytes: Pickle格式的字节数据
            
        Returns:
            反序列化后的数据
        """
        try:
            return pickle.loads(pickle_bytes)
        except Exception as e:
            print(f"从Pickle反序列化失败: {e}")
            return None 