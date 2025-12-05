"""
实用工具模块（组合模块）
整合书签和管理功能模块
"""
from typing import Dict, Any
from ..core.base_controller import BaseController
from .utility_bookmark import UtilityBookmarkModule
from .utility_management import UtilityManagementModule


class UtilityModule:
    """实用工具模块（组合模块）"""
    
    def __init__(self, base_controller: BaseController):
        self.base = base_controller
        self.bookmark = UtilityBookmarkModule(base_controller)
        self.management = UtilityManagementModule(base_controller)
    
    # 书签操作
    def add_bookmark(self, address: str, name: str = "") -> Dict[str, Any]:
        """添加地址书签"""
        return self.bookmark.add_bookmark(address, name)
    
    def remove_bookmark(self, address: str) -> Dict[str, Any]:
        """删除地址书签"""
        return self.bookmark.remove_bookmark(address)
    
    def get_bookmarks(self) -> Dict[str, Any]:
        """获取所有书签列表"""
        return self.bookmark.get_bookmarks()
    
    def goto_bookmark(self, name: str) -> Dict[str, Any]:
        """跳转到书签"""
        return self.bookmark.goto_bookmark(name)
    
    # 管理功能
    def load_file(self, file_path: str) -> Dict[str, Any]:
        """加载文件到调试器"""
        return self.management.load_file(file_path)
    
    def save_memory_to_file(self, address: str, size: int, output_file: str) -> Dict[str, Any]:
        """保存内存到文件"""
        return self.management.save_memory_to_file(address, size, output_file)
    
    def calculate_address(self, base_address: str, offset: int) -> Dict[str, Any]:
        """计算地址（基址+偏移）"""
        return self.management.calculate_address(base_address, offset)
    
    def format_address(self, address: str, format_type: str = "hex") -> Dict[str, Any]:
        """格式化地址"""
        return self.management.format_address(address, format_type)
    
    def save_script(self, script_content: str, file_path: str) -> Dict[str, Any]:
        """保存脚本到文件"""
        return self.management.save_script(script_content, file_path)
    
    def load_script(self, file_path: str) -> Dict[str, Any]:
        """从文件加载脚本"""
        return self.management.load_script(file_path)
    
    def get_script_history(self, count: int = 20) -> Dict[str, Any]:
        """获取脚本执行历史"""
        return self.management.get_script_history(count)
    
    def save_config(self, config_name: str) -> Dict[str, Any]:
        """保存当前调试配置"""
        return self.management.save_config(config_name)
    
    def load_config(self, config_name: str) -> Dict[str, Any]:
        """加载调试配置"""
        return self.management.load_config(config_name)
    
    def list_configs(self) -> Dict[str, Any]:
        """获取所有配置列表"""
        return self.management.list_configs()

