"""
内存模块（组合模块）
整合内存基础操作和高级操作模块
"""
from typing import Dict, Any, List, Optional
from ..core.base_controller import BaseController
from .memory_basic import MemoryBasicModule
from .memory_advanced import MemoryAdvancedModule


class MemoryModule:
    """内存操作模块（组合模块）"""
    
    def __init__(self, base_controller: BaseController):
        self.base = base_controller
        self.basic = MemoryBasicModule(base_controller)
        self.advanced = MemoryAdvancedModule(base_controller)
    
    # 基础操作
    def read_memory(self, address: str, size: int = 64) -> Dict[str, Any]:
        """读取内存"""
        return self.basic.read_memory(address, size)
    
    def write_memory(self, address: str, data: str) -> Dict[str, Any]:
        """写入内存"""
        return self.basic.write_memory(address, data)
    
    def search_memory(self, pattern: str, start: str = "", end: str = "") -> Dict[str, Any]:
        """搜索内存"""
        return self.basic.search_memory(pattern, start, end)
    
    def dump_memory(self, address: str, size: int, output_file: str = "") -> Dict[str, Any]:
        """内存转储功能"""
        return self.basic.dump_memory(address, size, output_file)
    
    # 高级操作
    def set_memory_protection(self, address: str, size: int, protection: str) -> Dict[str, Any]:
        """设置内存保护属性"""
        return self.advanced.set_memory_protection(address, size, protection)
    
    def get_memory_protection(self, address: str) -> Dict[str, Any]:
        """获取内存保护属性"""
        return self.advanced.get_memory_protection(address)
    
    def compare_memory(self, address1: str, address2: str, size: int) -> Dict[str, Any]:
        """比较两处内存内容"""
        return self.advanced.compare_memory(address1, address2, size)
    
    def fill_memory(self, address: str, size: int, value: int) -> Dict[str, Any]:
        """填充内存"""
        return self.advanced.fill_memory(address, size, value)
    
    def allocate_memory(self, size: int, protection: str = "RWX") -> Dict[str, Any]:
        """分配内存"""
        return self.advanced.allocate_memory(size, protection)
    
    def free_memory(self, address: str) -> Dict[str, Any]:
        """释放内存"""
        return self.advanced.free_memory(address)
    
    def get_memory_region_info(self, address: str) -> Dict[str, Any]:
        """获取内存区域信息"""
        return self.advanced.get_memory_region_info(address)
    
    def batch_read_memory(self, addresses: List[str], sizes: Optional[List[int]] = None) -> Dict[str, Any]:
        """批量读取内存"""
        return self.advanced.batch_read_memory(addresses, sizes)

