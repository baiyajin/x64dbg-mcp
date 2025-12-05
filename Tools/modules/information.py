"""
信息获取模块
提供信息获取相关的操作（模块、堆栈、调用栈、字符串、引用、导入导出等）
"""
from typing import Dict, Any
from ..core.base_controller import BaseController


class InformationModule:
    """信息获取模块"""
    
    def __init__(self, base_controller: BaseController):
        self.base = base_controller
    
    def get_modules(self) -> Dict[str, Any]:
        """获取模块列表"""
        return self.base.execute_command("mod")
    
    def get_stack(self, count: int = 10) -> Dict[str, Any]:
        """获取堆栈信息"""
        return self.base.execute_command(f"stack {count}")
    
    def get_call_stack(self, depth: int = 20) -> Dict[str, Any]:
        """获取调用栈"""
        return self.base.execute_command(f"callstack {depth}")
    
    def get_segments(self) -> Dict[str, Any]:
        """获取内存段信息"""
        return self.base.execute_command("mem")
    
    def get_strings(self, min_length: int = 4) -> Dict[str, Any]:
        """搜索字符串"""
        return self.base.execute_command(f"strref {min_length}")
    
    def get_references(self, address: str) -> Dict[str, Any]:
        """获取地址引用"""
        address = address.strip().replace(" ", "")
        return self.base.execute_command(f"xref {address}")
    
    def get_imports(self) -> Dict[str, Any]:
        """获取导入函数列表"""
        return self.base.execute_command("imp")
    
    def get_exports(self) -> Dict[str, Any]:
        """获取导出函数列表"""
        return self.base.execute_command("exp")

