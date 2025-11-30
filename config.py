# X64Dbg MCP 配置文件

# X64Dbg路径配置
# 请根据你的实际安装路径修改
X64DBG_PATH = r"C:\Program Files\x64dbg\release\x64\x64dbg.exe"
X64DBG_PLUGIN_DIR = r"C:\Program Files\x64dbg\release\x64\plugins"

# 如果x64dbg安装在默认位置，可以尝试自动检测
import os
if not os.path.exists(X64DBG_PATH):
    # 尝试其他常见路径
    common_paths = [
        r"C:\x64dbg\release\x64\x64dbg.exe",
        r"D:\x64dbg\release\x64\x64dbg.exe",
        os.path.join(os.path.expanduser("~"), "x64dbg", "release", "x64", "x64dbg.exe"),
    ]
    for path in common_paths:
        if os.path.exists(path):
            X64DBG_PATH = path
            X64DBG_PLUGIN_DIR = os.path.join(os.path.dirname(path), "plugins")
            break

# MCP服务器配置
MCP_HOST = "127.0.0.1"
MCP_PORT = 3000

# 调试配置
DEBUG_MODE = False

# 日志配置
LOG_LEVEL = "INFO"

