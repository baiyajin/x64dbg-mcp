"""
X64Dbg MCP Server
Model Context Protocol服务器，用于AI辅助逆向分析和调试
"""
import logging
import sys
import io
from fastmcp import FastMCP
from Tools.registry import register_tools

# 配置标准输入输出编码
stdin = sys.stdin
stdout = sys.stdout
if hasattr(stdin, 'reconfigure'):
    stdin.reconfigure(encoding='utf-8')
if hasattr(stdout, 'reconfigure'):
    stdout.reconfigure(encoding='utf-8')

# 配置stderr编码为UTF-8，避免中文乱码
if sys.stderr.encoding != 'utf-8':
    try:
        sys.stderr = io.TextIOWrapper(sys.stderr.buffer, encoding='utf-8', errors='replace')
    except (AttributeError, ValueError):
        # 如果无法重新配置，使用默认编码
        pass

# 配置日志 - 输出到stderr，避免干扰MCP协议的stdout JSON通信
logging.basicConfig(
    level=logging.WARNING,  # 只记录警告和错误，减少输出
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    handlers=[
        logging.StreamHandler(sys.stderr)  # 使用stderr而不是stdout
    ]
)
logger = logging.getLogger(__name__)

# 创建FastMCP实例
# 注意：FastMCP的启动横幅会输出到stderr，这是FastMCP库的正常行为
# 这些输出被Cursor标记为[error]但实际上不是错误，只是FastMCP的正常启动信息
mcp = FastMCP(
    "X64Dbg-MCP-Server",
    instructions='X64Dbg MCP服务，用于AI辅助逆向分析和调试',
    version='0.1.0'
)

# 注册工具
try:
    register_tools(mcp)
    # 不输出到stdout，避免干扰MCP协议
    # logger.info("X64Dbg工具注册成功")
except Exception as e:
    logger.error(f"工具注册失败: {e}", exc_info=True)

if __name__ == "__main__":
    # 不输出到stdout，避免干扰MCP协议
    # logger.info("启动X64Dbg MCP服务器...")
    # 设置log_level为ERROR以减少FastMCP的日志输出
    # 注意：FastMCP的启动横幅仍会输出到stderr，这是库的正常行为
    mcp.run(log_level='ERROR')

