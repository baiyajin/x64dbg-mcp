"""
X64Dbg MCP Server
Model Context Protocol服务器，用于AI辅助逆向分析和调试
"""
import logging
import sys
from fastmcp import FastMCP
from Tools.x64dbg_tools import register_tools

# 配置标准输入输出编码
stdin = sys.stdin
stdout = sys.stdout
if hasattr(stdin, 'reconfigure'):
    stdin.reconfigure(encoding='utf-8')
if hasattr(stdout, 'reconfigure'):
    stdout.reconfigure(encoding='utf-8')

# 配置日志
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    handlers=[
        logging.StreamHandler(sys.stdout)
    ]
)
logger = logging.getLogger(__name__)

# 创建FastMCP实例
mcp = FastMCP(
    "X64Dbg-MCP-Server",
    instructions='X64Dbg MCP服务，用于AI辅助逆向分析和调试',
    version='0.1.0'
)

# 注册工具
try:
    register_tools(mcp)
    logger.info("X64Dbg工具注册成功")
except Exception as e:
    logger.error(f"工具注册失败: {e}")

if __name__ == "__main__":
    logger.info("启动X64Dbg MCP服务器...")
    mcp.run()

