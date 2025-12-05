# X64Dbg MCP 配置示例文件
# 复制此文件为 config.py 并修改相应的配置

# X64Dbg路径配置
# 如果x64dbg未安装或路径不同，系统会自动尝试检测常见路径
# 如果都找不到，MCP服务器仍可启动，但工具调用时会提示需要配置路径

import os
from pathlib import Path

# 默认路径（用户自定义路径，优先使用）
# 请根据你的实际安装路径修改以下两行
DEFAULT_X64DBG_PATH = r"C:\Program Files\x64dbg\release\x64\x64dbg.exe"
DEFAULT_X64DBG_PLUGIN_DIR = r"C:\Program Files\x64dbg\release\x64\plugins"

def find_x64dbg_path():
    """
    自动检测x64dbg安装路径
    返回 (x64dbg_path, plugin_dir) 或 (None, None)
    """
    # 首先检查用户自定义路径
    if os.path.exists(DEFAULT_X64DBG_PATH):
        return DEFAULT_X64DBG_PATH, DEFAULT_X64DBG_PLUGIN_DIR
    
    # 尝试其他常见路径
    common_paths = [
        # 标准安装路径
        r"C:\Program Files\x64dbg\release\x64\x64dbg.exe",
        r"C:\Program Files (x86)\x64dbg\release\x64\x64dbg.exe",
        # 用户目录
        os.path.join(os.path.expanduser("~"), "x64dbg", "release", "x64", "x64dbg.exe"),
        # 其他常见位置
        r"C:\x64dbg\release\x64\x64dbg.exe",
        r"D:\x64dbg\release\x64\x64dbg.exe",
        r"E:\x64dbg\release\x64\x64dbg.exe",
        # 项目目录（开发环境）
        os.path.join(os.path.dirname(os.path.dirname(__file__)), "x64dbg", "release", "x64", "x64dbg.exe"),
    ]
    
    for path in common_paths:
        if os.path.exists(path):
            plugin_dir = os.path.join(os.path.dirname(path), "plugins")
            return path, plugin_dir
    
    # 尝试从环境变量获取
    env_path = os.environ.get("X64DBG_PATH")
    if env_path and os.path.exists(env_path):
        plugin_dir = os.path.join(os.path.dirname(env_path), "plugins")
        return env_path, plugin_dir
    
    return None, None

# 自动检测路径
X64DBG_PATH, X64DBG_PLUGIN_DIR = find_x64dbg_path()

# 验证路径有效性
X64DBG_INSTALLED = X64DBG_PATH is not None and os.path.exists(X64DBG_PATH)
X64DBG_PLUGIN_DIR_EXISTS = X64DBG_PLUGIN_DIR is not None and os.path.exists(X64DBG_PLUGIN_DIR)

# MCP服务器配置
MCP_HOST = "127.0.0.1"
MCP_PORT = 3000

# 调试配置
DEBUG_MODE = False

# 日志配置
LOG_LEVEL = "INFO"

