"""
工具注册模块
注册所有X64Dbg MCP工具
使用新的模块化控制器结构
"""
from ..x64dbg_controller import X64DbgController

# 创建全局控制器实例（使用新的模块化结构）
controller = X64DbgController()


def register_tools(mcp):
    """
    注册所有X64Dbg工具
    使用原来的register_tools函数，但替换为新的控制器
    """
    # 导入原来的register_tools函数
    from Tools import x64dbg_tools
    
    # 替换原来的controller为新的模块化controller
    original_controller = x64dbg_tools.controller
    x64dbg_tools.controller = controller
    
    try:
        # 调用原来的register_tools函数（它会注册所有工具）
        x64dbg_tools.register_tools(mcp)
    finally:
        # 恢复原来的controller（如果需要）
        x64dbg_tools.controller = original_controller

