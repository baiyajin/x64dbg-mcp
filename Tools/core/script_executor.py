"""
脚本执行模块
负责创建和执行x64dbg Python脚本
"""
import os
import tempfile
from typing import Dict, Any
from .result_parser import ResultParser


class ScriptExecutor:
    """脚本执行器"""
    
    def __init__(self, plugin_dir: str):
        """
        初始化脚本执行器
        
        :param plugin_dir: x64dbg插件目录
        """
        self.plugin_dir = plugin_dir
        self.temp_script_dir = os.path.join(self.plugin_dir, "mcp_temp")
        self.result_parser = ResultParser()
        
        # 确保临时脚本目录存在
        if not os.path.exists(self.temp_script_dir):
            try:
                os.makedirs(self.temp_script_dir, exist_ok=True)
            except Exception as e:
                print(f"警告: 无法创建临时脚本目录: {e}")
                self.temp_script_dir = tempfile.gettempdir()
    
    def create_script_file(self, script_content: str) -> str:
        """
        创建临时Python脚本文件
        
        :param script_content: 脚本内容
        :return: 脚本文件路径
        """
        script_file = os.path.join(self.temp_script_dir, f"mcp_cmd_{os.getpid()}.py")
        try:
            with open(script_file, 'w', encoding='utf-8') as f:
                f.write(script_content)
            return script_file
        except Exception as e:
            raise Exception(f"创建脚本文件失败: {str(e)}")
    
    def execute_script_auto(self, script_content: str, parse_result: bool = True) -> Dict[str, Any]:
        """
        自动执行脚本（通过插件API）
        尝试通过x64dbg的Python插件API自动执行脚本
        
        :param script_content: 要执行的脚本内容
        :param parse_result: 是否解析执行结果（默认True）
        :return: 执行结果
        """
        try:
            # 转义脚本内容中的特殊字符
            escaped_content = script_content.replace('\\', '\\\\').replace("'", "\\'").replace('"', '\\"')
            script_file_path = os.path.join(self.temp_script_dir, f"mcp_auto_{os.getpid()}.py")
            
            # 创建增强的脚本，尝试自动执行并捕获输出
            auto_script = f"""# X64Dbg MCP Auto Execute Script
import os
import sys
import io
import contextlib

# 捕获输出
output_buffer = io.StringIO()
try:
    # 尝试通过x64dbg Python API执行
    # 如果dbgcmd可用，说明在x64dbg环境中
    if 'dbgcmd' in globals() or 'dbg' in sys.modules:
        with contextlib.redirect_stdout(output_buffer), contextlib.redirect_stderr(output_buffer):
            exec(compile('''{escaped_content}''', '<string>', 'exec'))
        output = output_buffer.getvalue()
        # 如果脚本没有输出MCP_RESULT，添加一个
        if 'MCP_RESULT' not in output:
            print("MCP_RESULT:{{'status':'success','message':'脚本自动执行成功','output':'" + output.replace("'", "\\'")[:500] + "'}}")
    else:
        raise NameError("Not in x64dbg environment")
except NameError:
    # 如果不在x64dbg环境中，保存脚本文件
    script_file = r"{script_file_path}"
    with open(script_file, 'w', encoding='utf-8') as f:
        f.write('''{escaped_content}''')
    print(f"MCP_RESULT:{{'status':'pending','script_file':'{{script_file}}','message':'脚本已保存，请在x64dbg中加载执行'}}")
except Exception as e:
    import traceback
    error_msg = str(e) + "\\n" + traceback.format_exc()
    print(f"MCP_RESULT:{{'status':'error','error':'{{error_msg}}'}}")
"""
            script_file = self.create_script_file(auto_script)
            
            result = {
                "status": "success",
                "script_file": script_file,
                "message": "自动执行脚本已创建，如果x64dbg支持API调用将自动执行"
            }
            
            # 如果启用结果解析，尝试读取脚本输出（如果可用）
            if parse_result:
                result["parse_result"] = True
            
            return result
        except Exception as e:
            return {
                "status": "error",
                "message": f"创建自动执行脚本失败: {str(e)}"
            }

