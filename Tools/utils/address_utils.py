"""
地址工具模块
提供地址解析、格式化和计算功能
"""
from typing import Dict, Any, Optional


def parse_address(address: str) -> Optional[int]:
    """
    解析地址字符串为整数
    
    :param address: 地址字符串，可以是十六进制(0x401000)或十进制
    :return: 地址的整数值，如果解析失败返回None
    """
    if not address:
        return None
    
    address = address.strip().replace(" ", "")
    try:
        if address.startswith('0x') or address.startswith('0X'):
            return int(address, 16)
        else:
            return int(address)
    except ValueError:
        return None


def format_address(address: int, format_type: str = "hex") -> str:
    """
    格式化地址为字符串
    
    :param address: 地址整数值
    :param format_type: 格式类型，可选值: hex, decimal, octal, binary
    :return: 格式化后的地址字符串
    """
    formats = {
        "hex": hex(address),
        "decimal": str(address),
        "octal": oct(address),
        "binary": bin(address)
    }
    return formats.get(format_type.lower(), hex(address))


def calculate_address(base_address: str, offset: int) -> Dict[str, Any]:
    """
    计算地址（基址+偏移）
    
    :param base_address: 基址字符串
    :param offset: 偏移量（可以是负数）
    :return: 计算结果字典
    """
    base = parse_address(base_address)
    if base is None:
        return {
            "status": "error",
            "message": f"无法解析基址: {base_address}"
        }
    
    result_addr = base + offset
    return {
        "status": "success",
        "base_address": base_address,
        "offset": offset,
        "result_address": hex(result_addr),
        "result_decimal": result_addr
    }

