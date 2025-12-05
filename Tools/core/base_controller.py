"""
基础控制器模块
提供x64dbg命令执行的核心功能
"""
import subprocess
import os
from typing import Dict, Any
from .script_executor import ScriptExecutor
from .result_parser import ResultParser
import sys

# 添加项目根目录到路径
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__)))))
import config


class BaseController:
    """基础控制器，提供命令执行功能"""
    
    def __init__(self):
        """初始化基础控制器"""
        self.x64dbg_path = config.X64DBG_PATH
        self.plugin_dir = config.X64DBG_PLUGIN_DIR
        self.is_connected = False
        self.script_executor = ScriptExecutor(self.plugin_dir)
        self.result_parser = ResultParser()
    
    def execute_command(self, command: str, auto_execute: bool = True, parse_result: bool = True) -> Dict[str, Any]:
        """
        执行x64dbg命令
        通过创建Python脚本文件，x64dbg插件可以读取并执行
        如果auto_execute为True，尝试通过插件API自动执行
        
        :param command: 要执行的命令
        :param auto_execute: 是否尝试自动执行（默认True）
        :param parse_result: 是否解析执行结果（默认True）
        :return: 执行结果
        """
        try:
            # 转义命令中的特殊字符
            escaped_command = command.replace("'", "\\'").replace('"', '\\"')
            
            # 创建Python脚本内容
            if auto_execute:
                # 尝试自动执行的脚本，包含结果捕获
                script_content = f"""# X64Dbg MCP Command Script (Auto Execute)
# Command: {command}
import io
import contextlib

output_buffer = io.StringIO()
try:
    import dbg
    # 尝试通过API直接执行并捕获输出
    with contextlib.redirect_stdout(output_buffer), contextlib.redirect_stderr(output_buffer):
        result = dbgcmd('{escaped_command}')
    output = output_buffer.getvalue()
    
    # 构建结果，包含命令输出
    result_data = {{
        'status': 'success',
        'command': '{escaped_command}',
        'result': str(result) if result is not None else output,
        'output': output,
        'auto_executed': True
    }}
    print(f"MCP_RESULT:{{result_data}}")
except NameError:
    # 如果不在x64dbg环境中，保存脚本文件
    script_file = r"{self.script_executor.temp_script_dir}\\\\mcp_cmd_{os.getpid()}.py"
    script_code = '''# X64Dbg MCP Command Script
import io
import contextlib

output_buffer = io.StringIO()
try:
    with contextlib.redirect_stdout(output_buffer), contextlib.redirect_stderr(output_buffer):
        result = dbgcmd('{escaped_command}')
    output = output_buffer.getvalue()
    result_data = {{
        'status': 'success',
        'command': '{escaped_command}',
        'result': str(result) if result is not None else output,
        'output': output
    }}
    print(f"MCP_RESULT:{{result_data}}")
except Exception as e:
    print(f"MCP_RESULT:{{'status':'error','command':'{escaped_command}','error':str(e)}}")
'''
    with open(script_file, 'w', encoding='utf-8') as f:
        f.write(script_code)
    print(f"MCP_RESULT:{{'status':'pending','command':'{escaped_command}','script_file':'{{script_file}}','message':'脚本已保存，请在x64dbg中加载执行'}}")
except Exception as e:
    import traceback
    error_msg = str(e) + "\\n" + traceback.format_exc()
    print(f"MCP_RESULT:{{'status':'error','command':'{escaped_command}','error':'{{error_msg}}'}}")
"""
                result = self.script_executor.execute_script_auto(script_content, parse_result)
                if parse_result and "script_file" in result:
                    result["command"] = command
                    result["parse_result_enabled"] = True
                return result
            else:
                # 传统方式：仅创建脚本文件
                script_content = f"""# X64Dbg MCP Command Script
# Command: {command}
import io
import contextlib

output_buffer = io.StringIO()
try:
    with contextlib.redirect_stdout(output_buffer), contextlib.redirect_stderr(output_buffer):
        result = dbgcmd('{escaped_command}')
    output = output_buffer.getvalue()
    result_data = {{
        'status': 'success',
        'command': '{escaped_command}',
        'result': str(result) if result is not None else output,
        'output': output
    }}
    print(f"MCP_RESULT:{{result_data}}")
except Exception as e:
    print(f"MCP_RESULT:{{'status':'error','command':'{escaped_command}','error':str(e)}}")
"""
                script_file = self.script_executor.create_script_file(script_content)
                
                return {
                    "status": "success",
                    "command": command,
                    "script_file": script_file,
                    "parse_result_enabled": parse_result,
                    "message": f"命令脚本已创建: {command}。请在x64dbg中执行: File -> Script -> Load -> {os.path.basename(script_file)}"
                }
        except Exception as e:
            return {
                "status": "error",
                "message": f"执行命令失败: {str(e)}"
            }
    
    def execute_command_direct(self, command: str) -> Dict[str, Any]:
        """
        直接执行命令（如果x64dbg支持命令行参数）
        
        :param command: 要执行的命令
        :return: 执行结果
        """
        try:
            # 尝试通过命令行执行（需要x64dbg支持）
            # 注意：标准x64dbg可能不支持此方式，需要插件支持
            result = subprocess.run(
                [self.x64dbg_path, "-script", command],
                capture_output=True,
                text=True,
                timeout=10
            )
            
            return {
                "status": "success",
                "command": command,
                "output": result.stdout,
                "error": result.stderr
            }
        except subprocess.TimeoutExpired:
            return {
                "status": "error",
                "message": "命令执行超时"
            }
        except Exception as e:
            return {
                "status": "error",
                "message": f"执行命令失败: {str(e)}"
            }

