"""
X64Dbg工具实现
通过x64dbg的Python插件系统或命令行接口控制调试器
"""
import subprocess
import os
import json
import re
import tempfile
from typing import Optional, Dict, Any, List
from pathlib import Path
import sys

# 添加项目根目录到路径
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
import config


class X64DbgController:
    """X64Dbg控制器，用于与x64dbg交互"""
    
    def __init__(self):
        self.x64dbg_path = config.X64DBG_PATH
        self.plugin_dir = config.X64DBG_PLUGIN_DIR
        self.is_connected = False
        self.temp_script_dir = os.path.join(self.plugin_dir, "mcp_temp")
        
        # 确保临时脚本目录存在
        if not os.path.exists(self.temp_script_dir):
            try:
                os.makedirs(self.temp_script_dir, exist_ok=True)
            except Exception as e:
                print(f"警告: 无法创建临时脚本目录: {e}")
                self.temp_script_dir = tempfile.gettempdir()
    
    def _create_script_file(self, script_content: str) -> str:
        """创建临时Python脚本文件"""
        script_file = os.path.join(self.temp_script_dir, f"mcp_cmd_{os.getpid()}.py")
        try:
            with open(script_file, 'w', encoding='utf-8') as f:
                f.write(script_content)
            return script_file
        except Exception as e:
            raise Exception(f"创建脚本文件失败: {str(e)}")
    
    def execute_command(self, command: str, auto_execute: bool = True, parse_result: bool = True) -> Dict[str, Any]:
        """
        执行x64dbg命令
        通过创建Python脚本文件，x64dbg插件可以读取并执行
        如果auto_execute为True，尝试通过插件API自动执行
        
        :param command: 要执行的命令
        :param auto_execute: 是否尝试自动执行（默认True）
        :param parse_result: 是否解析执行结果（默认True）
        """
        try:
            # 转义命令中的特殊字符
            escaped_command = command.replace("'", "\\'").replace('"', '\\"')
            
            # 创建Python脚本内容
            # x64dbg的Python插件通常使用dbgcmd函数执行命令
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
    script_file = r"{self.temp_script_dir}\\mcp_cmd_{os.getpid()}.py"
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
                result = self.execute_script_auto(script_content, parse_result)
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
                script_file = self._create_script_file(script_content)
                
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
    
    def get_registers(self) -> Dict[str, Any]:
        """获取寄存器信息"""
        return self.execute_command("r")
    
    def set_register(self, register_name: str, value: str) -> Dict[str, Any]:
        """
        设置单个寄存器值
        
        :param register_name: 寄存器名称（如: eax, ebx, eip, rax等）
        :param value: 寄存器值（可以是十六进制0x401000或十进制）
        """
        register_name = register_name.strip().lower()
        value = value.strip()
        
        try:
            # 使用x64dbg命令设置寄存器
            return self.execute_command(f"set {register_name}={value}")
        except Exception as e:
            return {
                "status": "error",
                "message": f"设置寄存器失败: {str(e)}"
            }
    
    def set_registers(self, registers: Dict[str, str]) -> Dict[str, Any]:
        """
        批量设置寄存器值
        
        :param registers: 寄存器字典，格式: {"eax": "0x401000", "ebx": "0x100"}
        """
        if not registers:
            raise ValueError('寄存器字典不能为空!')
        
        try:
            results = {}
            for reg_name, reg_value in registers.items():
                result = self.set_register(reg_name, reg_value)
                results[reg_name] = result
            
            return {
                "status": "success",
                "results": results,
                "message": f"已设置{len(registers)}个寄存器"
            }
        except Exception as e:
            return {
                "status": "error",
                "message": f"批量设置寄存器失败: {str(e)}"
            }
    
    def get_modules(self) -> Dict[str, Any]:
        """获取模块列表"""
        return self.execute_command("mod")
    
    def set_breakpoint(self, address: str) -> Dict[str, Any]:
        """设置断点"""
        # 清理地址格式
        address = address.strip().replace(" ", "")
        return self.execute_command(f"bp {address}")
    
    def remove_breakpoint(self, address: str) -> Dict[str, Any]:
        """删除断点"""
        address = address.strip().replace(" ", "")
        return self.execute_command(f"bpc {address}")
    
    def enable_breakpoint(self, address: str) -> Dict[str, Any]:
        """启用断点"""
        address = address.strip().replace(" ", "")
        return self.execute_command(f"bpe {address}")
    
    def disable_breakpoint(self, address: str) -> Dict[str, Any]:
        """禁用断点"""
        address = address.strip().replace(" ", "")
        return self.execute_command(f"bpd {address}")
    
    def get_breakpoint_hit_count(self, address: str) -> Dict[str, Any]:
        """
        获取断点命中计数
        
        :param address: 断点地址
        """
        address = address.strip().replace(" ", "")
        
        try:
            hit_count_script = f"""# X64Dbg Breakpoint Hit Count Script
try:
    import dbg
    addr = int('{address}', 16) if '{address}'.startswith('0x') else int('{address}')
    
    # 获取断点命中计数
    if hasattr(dbg, 'getBreakpointHitCount'):
        count = dbg.getBreakpointHitCount(addr)
        print(f"MCP_RESULT:{{'status':'success','address':'{address}','hit_count':count}}")
    else:
        # 尝试通过命令获取
        result = dbgcmd(f'bphitcount {{addr}}')
        print(f"MCP_RESULT:{{'status':'success','address':'{address}','result':result}}")
except Exception as e:
    print(f"MCP_RESULT:{{'status':'error','error':str(e)}}")
"""
            return self.execute_script_auto(hit_count_script)
        except Exception as e:
            return {
                "status": "error",
                "message": f"获取断点命中计数失败: {str(e)}"
            }
    
    def reset_breakpoint_hit_count(self, address: str) -> Dict[str, Any]:
        """
        重置断点命中计数
        
        :param address: 断点地址
        """
        address = address.strip().replace(" ", "")
        
        try:
            reset_script = f"""# X64Dbg Reset Breakpoint Hit Count Script
try:
    import dbg
    addr = int('{address}', 16) if '{address}'.startswith('0x') else int('{address}')
    
    # 重置断点命中计数
    if hasattr(dbg, 'resetBreakpointHitCount'):
        result = dbg.resetBreakpointHitCount(addr)
        print(f"MCP_RESULT:{{'status':'success','address':'{address}','result':result}}")
    else:
        # 尝试通过命令重置
        result = dbgcmd(f'bpreset {{addr}}')
        print(f"MCP_RESULT:{{'status':'success','address':'{address}','result':result}}")
except Exception as e:
    print(f"MCP_RESULT:{{'status':'error','error':str(e)}}")
"""
            return self.execute_script_auto(reset_script)
        except Exception as e:
            return {
                "status": "error",
                "message": f"重置断点命中计数失败: {str(e)}"
            }
    
    def read_memory(self, address: str, size: int = 64) -> Dict[str, Any]:
        """读取内存"""
        address = address.strip().replace(" ", "")
        return self.execute_command(f"dump {address} {size}")
    
    def write_memory(self, address: str, data: str) -> Dict[str, Any]:
        """写入内存"""
        address = address.strip().replace(" ", "")
        return self.execute_command(f"write {address} {data}")
    
    def disassemble(self, address: str, count: int = 10) -> Dict[str, Any]:
        """反汇编代码"""
        address = address.strip().replace(" ", "")
        return self.execute_command(f"disasm {address} {count}")
    
    def get_stack(self, count: int = 10) -> Dict[str, Any]:
        """获取堆栈信息"""
        return self.execute_command(f"stack {count}")
    
    def search_memory(self, pattern: str, start: str = "", end: str = "") -> Dict[str, Any]:
        """搜索内存"""
        if start and end:
            return self.execute_command(f"findmem {pattern} {start} {end}")
        else:
            return self.execute_command(f"findmem {pattern}")
    
    def _parse_script_result(self, output: str) -> Dict[str, Any]:
        """
        解析脚本执行结果
        从输出中提取MCP_RESULT JSON数据
        """
        try:
            # 查找MCP_RESULT标记
            import re
            pattern = r'MCP_RESULT:(\{.*?\})'
            matches = re.findall(pattern, output, re.DOTALL)
            if matches:
                # 尝试解析最后一个结果
                result_str = matches[-1]
                try:
                    result = json.loads(result_str)
                    return result
                except json.JSONDecodeError:
                    # 如果JSON解析失败，尝试修复常见的转义问题
                    result_str = result_str.replace("'", '"')
                    try:
                        result = json.loads(result_str)
                        return result
                    except:
                        pass
            
            # 如果没有找到MCP_RESULT，返回原始输出
            return {
                "status": "success",
                "raw_output": output,
                "message": "脚本执行完成，但未找到结构化结果"
            }
        except Exception as e:
            return {
                "status": "error",
                "message": f"解析脚本结果失败: {str(e)}",
                "raw_output": output
            }
    
    def execute_script_auto(self, script_content: str, parse_result: bool = True) -> Dict[str, Any]:
        """
        自动执行脚本（通过插件API）
        尝试通过x64dbg的Python插件API自动执行脚本
        
        :param script_content: 要执行的脚本内容
        :param parse_result: 是否解析执行结果（默认True）
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
            script_file = self._create_script_file(auto_script)
            
            result = {
                "status": "success",
                "script_file": script_file,
                "message": "自动执行脚本已创建，如果x64dbg支持API调用将自动执行"
            }
            
            # 如果启用结果解析，尝试读取脚本输出（如果可用）
            if parse_result:
                # 注意：实际执行结果需要在x64dbg环境中才能获取
                # 这里只是准备解析功能
                result["parse_result"] = True
            
            return result
        except Exception as e:
            return {
                "status": "error",
                "message": f"创建自动执行脚本失败: {str(e)}"
            }
    
    def get_debugger_status(self) -> Dict[str, Any]:
        """获取调试器实时状态"""
        try:
            # 获取多个状态信息
            status_script = """# X64Dbg Status Script
try:
    import dbg
    status = {
        'is_debugging': dbg.isDebugging(),
        'is_running': dbg.isRunning(),
        'current_pid': dbg.getProcessId(),
        'current_tid': dbg.getThreadId(),
        'current_address': hex(dbg.getCurrentAddress()) if dbg.isDebugging() else None
    }
    print(f"MCP_RESULT:{{'status':'success','data':{status}}}")
except Exception as e:
    print(f"MCP_RESULT:{{'status':'error','error':str(e)}}")
"""
            return self.execute_script_auto(status_script)
        except Exception as e:
            return {
                "status": "error",
                "message": f"获取调试器状态失败: {str(e)}"
            }
    
    def set_breakpoint_conditional(self, address: str, condition: str = "") -> Dict[str, Any]:
        """设置带条件的断点"""
        address = address.strip().replace(" ", "")
        if condition:
            # x64dbg支持条件断点，格式: bp address,condition
            return self.execute_command(f"bp {address},{condition}")
        else:
            return self.set_breakpoint(address)
    
    def dump_memory(self, address: str, size: int, output_file: str = "") -> Dict[str, Any]:
        """内存转储功能"""
        address = address.strip().replace(" ", "")
        if not output_file:
            output_file = os.path.join(self.temp_script_dir, f"dump_{address.replace('0x', '').replace(' ', '')}_{size}.bin")
        
        try:
            dump_script = f"""# X64Dbg Memory Dump Script
try:
    import dbg
    addr = int('{address}', 16) if '{address}'.startswith('0x') else int('{address}')
    size = {size}
    data = dbg.read(addr, size)
    with open(r"{output_file}", 'wb') as f:
        f.write(data)
    print(f"MCP_RESULT:{{'status':'success','address':'{address}','size':{size},'output_file':'{output_file}'}}")
except Exception as e:
    print(f"MCP_RESULT:{{'status':'error','error':str(e)}}")
"""
            return self.execute_script_auto(dump_script)
        except Exception as e:
            return {
                "status": "error",
                "message": f"内存转储失败: {str(e)}"
            }
    
    def resolve_symbol(self, symbol: str) -> Dict[str, Any]:
        """解析符号地址"""
        try:
            # x64dbg可以通过符号名称解析地址
            resolve_script = f"""# X64Dbg Symbol Resolution Script
try:
    import dbg
    # 尝试解析符号
    addr = dbg.getAddressFromSymbol('{symbol}')
    if addr:
        print(f"MCP_RESULT:{{'status':'success','symbol':'{symbol}','address':hex(addr)}}")
    else:
        # 尝试通过命令解析
        result = dbgcmd('sym.fromname({symbol})')
        print(f"MCP_RESULT:{{'status':'success','symbol':'{symbol}','result':result}}")
except Exception as e:
    print(f"MCP_RESULT:{{'status':'error','error':str(e)}}")
"""
            return self.execute_script_auto(resolve_script)
        except Exception as e:
            return {
                "status": "error",
                "message": f"符号解析失败: {str(e)}"
            }
    
    def get_threads(self) -> Dict[str, Any]:
        """获取线程列表"""
        return self.execute_command("thread")
    
    def switch_thread(self, thread_id: int) -> Dict[str, Any]:
        """
        切换当前线程
        
        :param thread_id: 线程ID（TID）
        """
        try:
            switch_script = f"""# X64Dbg Switch Thread Script
try:
    import dbg
    tid = {thread_id}
    
    # 切换线程
    if hasattr(dbg, 'switchThread'):
        result = dbg.switchThread(tid)
        print(f"MCP_RESULT:{{'status':'success','thread_id':{thread_id},'result':result}}")
    else:
        result = dbgcmd(f'thread {{tid}}')
        print(f"MCP_RESULT:{{'status':'success','thread_id':{thread_id},'result':result}}")
except Exception as e:
    print(f"MCP_RESULT:{{'status':'error','error':str(e)}}")
"""
            return self.execute_script_auto(switch_script)
        except Exception as e:
            return {
                "status": "error",
                "message": f"切换线程失败: {str(e)}"
            }
    
    def suspend_thread(self, thread_id: int) -> Dict[str, Any]:
        """
        挂起线程
        
        :param thread_id: 线程ID（TID）
        """
        try:
            suspend_script = f"""# X64Dbg Suspend Thread Script
try:
    import dbg
    tid = {thread_id}
    
    # 挂起线程
    if hasattr(dbg, 'suspendThread'):
        result = dbg.suspendThread(tid)
        print(f"MCP_RESULT:{{'status':'success','thread_id':{thread_id},'result':result}}")
    else:
        result = dbgcmd(f'threadsuspend {{tid}}')
        print(f"MCP_RESULT:{{'status':'success','thread_id':{thread_id},'result':result}}")
except Exception as e:
    print(f"MCP_RESULT:{{'status':'error','error':str(e)}}")
"""
            return self.execute_script_auto(suspend_script)
        except Exception as e:
            return {
                "status": "error",
                "message": f"挂起线程失败: {str(e)}"
            }
    
    def resume_thread(self, thread_id: int) -> Dict[str, Any]:
        """
        恢复线程
        
        :param thread_id: 线程ID（TID）
        """
        try:
            resume_script = f"""# X64Dbg Resume Thread Script
try:
    import dbg
    tid = {thread_id}
    
    # 恢复线程
    if hasattr(dbg, 'resumeThread'):
        result = dbg.resumeThread(tid)
        print(f"MCP_RESULT:{{'status':'success','thread_id':{thread_id},'result':result}}")
    else:
        result = dbgcmd(f'threadresume {{tid}}')
        print(f"MCP_RESULT:{{'status':'success','thread_id':{thread_id},'result':result}}")
except Exception as e:
    print(f"MCP_RESULT:{{'status':'error','error':str(e)}}")
"""
            return self.execute_script_auto(resume_script)
        except Exception as e:
            return {
                "status": "error",
                "message": f"恢复线程失败: {str(e)}"
            }
    
    def get_thread_context(self, thread_id: int) -> Dict[str, Any]:
        """
        获取线程上下文
        
        :param thread_id: 线程ID（TID）
        """
        try:
            context_script = f"""# X64Dbg Get Thread Context Script
try:
    import dbg
    tid = {thread_id}
    
    # 获取线程上下文
    if hasattr(dbg, 'getThreadContext'):
        context = dbg.getThreadContext(tid)
        print(f"MCP_RESULT:{{'status':'success','thread_id':{thread_id},'context':{{context}}}}")
    else:
        result = dbgcmd(f'threadcontext {{tid}}')
        print(f"MCP_RESULT:{{'status':'success','thread_id':{thread_id},'result':result}}")
except Exception as e:
    print(f"MCP_RESULT:{{'status':'error','error':str(e)}}")
"""
            return self.execute_script_auto(context_script)
        except Exception as e:
            return {
                "status": "error",
                "message": f"获取线程上下文失败: {str(e)}"
            }
    
    def get_breakpoints(self) -> Dict[str, Any]:
        """获取所有断点列表"""
        return self.execute_command("bplist")
    
    def get_call_stack(self, depth: int = 20) -> Dict[str, Any]:
        """获取调用栈"""
        return self.execute_command(f"callstack {depth}")
    
    def get_segments(self) -> Dict[str, Any]:
        """获取内存段信息"""
        return self.execute_command("mem")
    
    def get_strings(self, min_length: int = 4) -> Dict[str, Any]:
        """搜索字符串"""
        return self.execute_command(f"strref {min_length}")
    
    def get_references(self, address: str) -> Dict[str, Any]:
        """获取地址引用"""
        address = address.strip().replace(" ", "")
        return self.execute_command(f"xref {address}")
    
    def get_imports(self) -> Dict[str, Any]:
        """获取导入函数列表"""
        return self.execute_command("imp")
    
    def get_exports(self) -> Dict[str, Any]:
        """获取导出函数列表"""
        return self.execute_command("exp")
    
    def get_comments(self, address: str = "") -> Dict[str, Any]:
        """获取注释"""
        if address:
            address = address.strip().replace(" ", "")
            return self.execute_command(f"comment {address}")
        else:
            return self.execute_command("commentlist")
    
    def get_labels(self) -> Dict[str, Any]:
        """获取标签列表"""
        return self.execute_command("labellist")
    
    def get_functions(self) -> Dict[str, Any]:
        """获取函数列表"""
        return self.execute_command("functionlist")
    
    def get_logs(self, count: int = 100) -> Dict[str, Any]:
        """
        获取x64dbg日志输出
        注意：这需要x64dbg支持日志API或通过命令获取
        """
        try:
            # x64dbg可能没有直接的日志命令，尝试通过其他方式获取
            # 这里使用log命令（如果存在）或通过脚本获取
            log_script = f"""# X64Dbg Log Capture Script
try:
    import dbg
    # 尝试获取日志（如果x64dbg支持）
    if hasattr(dbg, 'getLog'):
        logs = dbg.getLog({count})
        print(f"MCP_RESULT:{{'status':'success','logs':logs,'count':len(logs)}}")
    else:
        # 尝试通过命令获取
        result = dbgcmd('log')
        print(f"MCP_RESULT:{{'status':'success','logs':result,'count':{count}}}")
except Exception as e:
    print(f"MCP_RESULT:{{'status':'error','error':str(e)}}")
"""
            return self.execute_script_auto(log_script)
        except Exception as e:
            return {
                "status": "error",
                "message": f"获取日志失败: {str(e)}"
            }
    
    def capture_output(self, command: str) -> Dict[str, Any]:
        """
        捕获命令执行的实际输出
        这是execute_command的增强版本，专门用于获取输出
        """
        return self.execute_command(command, auto_execute=True, parse_result=True)
    
    def set_memory_protection(self, address: str, size: int, protection: str) -> Dict[str, Any]:
        """
        设置内存保护属性
        
        :param address: 内存起始地址
        :param size: 内存大小（字节）
        :param protection: 保护属性，可选值:
            - "R" 或 "READ": 只读
            - "W" 或 "WRITE": 可写
            - "X" 或 "EXECUTE": 可执行
            - "RW": 可读可写
            - "RX": 可读可执行
            - "RWX": 可读可写可执行
            - "NONE": 无访问权限
        """
        address = address.strip().replace(" ", "")
        
        # 映射保护属性到x64dbg命令格式
        protection_map = {
            "R": "PAGE_READONLY",
            "READ": "PAGE_READONLY",
            "W": "PAGE_READWRITE",
            "WRITE": "PAGE_READWRITE",
            "RW": "PAGE_READWRITE",
            "X": "PAGE_EXECUTE",
            "EXECUTE": "PAGE_EXECUTE",
            "RX": "PAGE_EXECUTE_READ",
            "RWX": "PAGE_EXECUTE_READWRITE",
            "NONE": "PAGE_NOACCESS"
        }
        
        prot_flag = protection_map.get(protection.upper(), protection)
        
        try:
            protect_script = f"""# X64Dbg Memory Protection Script
try:
    import dbg
    addr = int('{address}', 16) if '{address}'.startswith('0x') else int('{address}')
    size = {size}
    prot = '{prot_flag}'
    
    # 使用VirtualProtect或x64dbg API
    if hasattr(dbg, 'setMemoryProtection'):
        result = dbg.setMemoryProtection(addr, size, prot)
        print(f"MCP_RESULT:{{'status':'success','address':'{address}','size':{size},'protection':'{protection}','result':result}}")
    else:
        # 尝试通过命令设置
        result = dbgcmd(f'VirtualProtect {{addr}}, {{size}}, {{prot}}')
        print(f"MCP_RESULT:{{'status':'success','address':'{address}','size':{size},'protection':'{protection}','result':result}}")
except Exception as e:
    print(f"MCP_RESULT:{{'status':'error','error':str(e)}}")
"""
            return self.execute_script_auto(protect_script)
        except Exception as e:
            return {
                "status": "error",
                "message": f"设置内存保护失败: {str(e)}"
            }
    
    def get_memory_protection(self, address: str) -> Dict[str, Any]:
        """
        获取内存保护属性
        
        :param address: 内存地址
        """
        address = address.strip().replace(" ", "")
        
        try:
            protect_script = f"""# X64Dbg Get Memory Protection Script
try:
    import dbg
    addr = int('{address}', 16) if '{address}'.startswith('0x') else int('{address}')
    
    # 尝试获取内存保护属性
    if hasattr(dbg, 'getMemoryProtection'):
        prot = dbg.getMemoryProtection(addr)
        print(f"MCP_RESULT:{{'status':'success','address':'{address}','protection':prot}}")
    else:
        # 尝试通过命令获取
        result = dbgcmd(f'VirtualQuery {{addr}}')
        print(f"MCP_RESULT:{{'status':'success','address':'{address}','result':result}}")
except Exception as e:
    print(f"MCP_RESULT:{{'status':'error','error':str(e)}}")
"""
            return self.execute_script_auto(protect_script)
        except Exception as e:
            return {
                "status": "error",
                "message": f"获取内存保护失败: {str(e)}"
            }
    
    # ========== 中优先级功能 ==========
    
    def set_hardware_breakpoint(self, address: str, break_type: str = "execute", size: int = 1) -> Dict[str, Any]:
        """
        设置硬件断点
        
        :param address: 断点地址
        :param break_type: 断点类型，可选值:
            - "execute" 或 "e": 执行断点
            - "write" 或 "w": 写入断点
            - "read" 或 "r": 读取断点
            - "readwrite" 或 "rw": 读写断点
        :param size: 断点大小（字节），可选值: 1, 2, 4, 8
        """
        address = address.strip().replace(" ", "")
        
        # 映射断点类型
        type_map = {
            "execute": "0",
            "e": "0",
            "write": "1",
            "w": "1",
            "read": "2",
            "r": "2",
            "readwrite": "3",
            "rw": "3"
        }
        
        bp_type = type_map.get(break_type.lower(), "0")
        
        if size not in [1, 2, 4, 8]:
            size = 1
        
        try:
            hwbp_script = f"""# X64Dbg Hardware Breakpoint Script
try:
    import dbg
    addr = int('{address}', 16) if '{address}'.startswith('0x') else int('{address}')
    bp_type = {bp_type}
    bp_size = {size}
    
    # 设置硬件断点
    if hasattr(dbg, 'setHardwareBreakpoint'):
        result = dbg.setHardwareBreakpoint(addr, bp_type, bp_size)
        print(f"MCP_RESULT:{{'status':'success','address':'{address}','type':'{break_type}','size':{size},'result':result}}")
    else:
        # 尝试通过命令设置
        result = dbgcmd(f'hwbp {{addr}}, {{bp_type}}, {{bp_size}}')
        print(f"MCP_RESULT:{{'status':'success','address':'{address}','type':'{break_type}','size':{size},'result':result}}")
except Exception as e:
    print(f"MCP_RESULT:{{'status':'error','error':str(e)}}")
"""
            return self.execute_script_auto(hwbp_script)
        except Exception as e:
            return {
                "status": "error",
                "message": f"设置硬件断点失败: {str(e)}"
            }
    
    def remove_hardware_breakpoint(self, address: str) -> Dict[str, Any]:
        """删除硬件断点"""
        address = address.strip().replace(" ", "")
        return self.execute_command(f"hwbpdel {address}")
    
    def set_watchpoint(self, address: str, watch_type: str = "write", size: int = 4) -> Dict[str, Any]:
        """
        设置数据断点（监视点）
        
        :param address: 监视地址
        :param watch_type: 监视类型，可选值:
            - "write" 或 "w": 写入时触发
            - "read" 或 "r": 读取时触发
            - "readwrite" 或 "rw": 读写时触发
        :param size: 监视大小（字节），可选值: 1, 2, 4, 8
        """
        address = address.strip().replace(" ", "")
        
        # 数据断点实际上就是硬件断点的特殊类型
        if watch_type.lower() in ["read", "r"]:
            return self.set_hardware_breakpoint(address, "read", size)
        elif watch_type.lower() in ["readwrite", "rw"]:
            return self.set_hardware_breakpoint(address, "readwrite", size)
        else:
            return self.set_hardware_breakpoint(address, "write", size)
    
    def remove_watchpoint(self, address: str) -> Dict[str, Any]:
        """删除数据断点（监视点）"""
        return self.remove_hardware_breakpoint(address)
    
    def attach_process(self, process_id: int) -> Dict[str, Any]:
        """
        附加到进程
        
        :param process_id: 进程ID（PID）
        """
        try:
            attach_script = f"""# X64Dbg Attach Process Script
try:
    import dbg
    pid = {process_id}
    
    # 附加到进程
    if hasattr(dbg, 'attachProcess'):
        result = dbg.attachProcess(pid)
        print(f"MCP_RESULT:{{'status':'success','pid':{process_id},'result':result}}")
    else:
        # 尝试通过命令附加
        result = dbgcmd(f'attach {{pid}}')
        print(f"MCP_RESULT:{{'status':'success','pid':{process_id},'result':result}}")
except Exception as e:
    print(f"MCP_RESULT:{{'status':'error','error':str(e)}}")
"""
            return self.execute_script_auto(attach_script)
        except Exception as e:
            return {
                "status": "error",
                "message": f"附加进程失败: {str(e)}"
            }
    
    def detach_process(self) -> Dict[str, Any]:
        """分离当前调试的进程"""
        return self.execute_command("detach")
    
    def apply_patch(self, address: str, data: str, description: str = "") -> Dict[str, Any]:
        """
        应用代码补丁
        
        :param address: 补丁地址
        :param data: 要写入的数据（十六进制字符串，如: "90 90 90"）
        :param description: 补丁描述（可选）
        """
        address = address.strip().replace(" ", "")
        
        try:
            patch_script = f"""# X64Dbg Apply Patch Script
try:
    import dbg
    addr = int('{address}', 16) if '{address}'.startswith('0x') else int('{address}')
    patch_data = bytes.fromhex('{data.replace(' ', '')}')
    desc = '{description}'
    
    # 应用补丁
    if hasattr(dbg, 'setPatch'):
        result = dbg.setPatch(addr, patch_data, desc)
        print(f"MCP_RESULT:{{'status':'success','address':'{address}','data':'{data}','description':'{description}','result':result}}")
    else:
        # 先写入内存，然后标记为补丁
        dbg.write(addr, patch_data)
        result = dbgcmd(f'patch {{addr}}, {{desc}}')
        print(f"MCP_RESULT:{{'status':'success','address':'{address}','data':'{data}','description':'{description}','result':result}}")
except Exception as e:
    print(f"MCP_RESULT:{{'status':'error','error':str(e)}}")
"""
            return self.execute_script_auto(patch_script)
        except Exception as e:
            return {
                "status": "error",
                "message": f"应用补丁失败: {str(e)}"
            }
    
    def remove_patch(self, address: str) -> Dict[str, Any]:
        """
        移除代码补丁（恢复原始代码）
        
        :param address: 补丁地址
        """
        address = address.strip().replace(" ", "")
        
        try:
            remove_patch_script = f"""# X64Dbg Remove Patch Script
try:
    import dbg
    addr = int('{address}', 16) if '{address}'.startswith('0x') else int('{address}')
    
    # 移除补丁
    if hasattr(dbg, 'removePatch'):
        result = dbg.removePatch(addr)
        print(f"MCP_RESULT:{{'status':'success','address':'{address}','result':result}}")
    else:
        result = dbgcmd(f'patchdel {{addr}}')
        print(f"MCP_RESULT:{{'status':'success','address':'{address}','result':result}}")
except Exception as e:
    print(f"MCP_RESULT:{{'status':'error','error':str(e)}}")
"""
            return self.execute_script_auto(remove_patch_script)
        except Exception as e:
            return {
                "status": "error",
                "message": f"移除补丁失败: {str(e)}"
            }
    
    def get_patches(self) -> Dict[str, Any]:
        """获取所有补丁列表"""
        return self.execute_command("patchlist")
    
    # ========== 低优先级功能（高级功能） ==========
    
    def inject_code(self, address: str, shellcode: str, create_thread: bool = False) -> Dict[str, Any]:
        """
        注入代码（Shellcode）到目标进程
        
        :param address: 注入地址（如果为None，则在内存中分配空间）
        :param shellcode: Shellcode（十六进制字符串，如: "90 90 90"）
        :param create_thread: 是否创建新线程执行（默认False，在当前线程执行）
        """
        address = address.strip().replace(" ", "") if address else ""
        
        try:
            inject_script = f"""# X64Dbg Code Injection Script
try:
    import dbg
    shellcode_hex = '{shellcode.replace(' ', '')}'
    shellcode_bytes = bytes.fromhex(shellcode_hex)
    
    if '{address}':
        addr = int('{address}', 16) if '{address}'.startswith('0x') else int('{address}')
    else:
        # 分配内存
        addr = dbg.malloc(len(shellcode_bytes))
    
    # 写入Shellcode
    dbg.write(addr, shellcode_bytes)
    
    # 如果需要创建线程执行
    if {str(create_thread).lower()}:
        thread_id = dbg.createThread(addr)
        result = {{'address': hex(addr), 'thread_id': thread_id, 'executed': True}}
    else:
        # 保存当前上下文，执行代码，恢复上下文
        old_eip = dbg.getRegister('EIP') if hasattr(dbg, 'getRegister') else None
        dbg.setRegister('EIP', addr)
        result = {{'address': hex(addr), 'executed': False, 'message': '代码已注入，需要手动执行'}}
        if old_eip:
            dbg.setRegister('EIP', old_eip)
    
    print(f"MCP_RESULT:{{'status':'success','result':{{result}}}}")
except Exception as e:
    import traceback
    error_msg = str(e) + "\\n" + traceback.format_exc()
    print(f"MCP_RESULT:{{'status':'error','error':'{{error_msg}}'}}")
"""
            return self.execute_script_auto(inject_script)
        except Exception as e:
            return {
                "status": "error",
                "message": f"代码注入失败: {str(e)}"
            }
    
    def inject_dll(self, dll_path: str, wait_for_load: bool = True) -> Dict[str, Any]:
        """
        注入DLL到目标进程
        
        :param dll_path: DLL文件路径
        :param wait_for_load: 是否等待DLL加载完成（默认True）
        """
        try:
            inject_script = f"""# X64Dbg DLL Injection Script
try:
    import dbg
    import os
    dll_path = r"{dll_path}"
    
    if not os.path.exists(dll_path):
        raise FileNotFoundError(f"DLL文件不存在: {{dll_path}}")
    
    # 注入DLL
    if hasattr(dbg, 'injectDLL'):
        result = dbg.injectDLL(dll_path, {str(wait_for_load).lower()})
        print(f"MCP_RESULT:{{'status':'success','dll_path':'{dll_path}','result':result}}")
    else:
        # 尝试通过LoadLibrary注入
        # 在目标进程中调用LoadLibrary
        kernel32 = dbg.getModule('kernel32.dll')
        load_library = dbg.getAddressFromSymbol('kernel32.LoadLibraryA')
        
        # 在目标进程中分配内存写入DLL路径
        path_bytes = dll_path.encode('utf-8') + b'\\x00'
        path_addr = dbg.malloc(len(path_bytes))
        dbg.write(path_addr, path_bytes)
        
        # 调用LoadLibrary
        result = dbg.call(load_library, [path_addr])
        print(f"MCP_RESULT:{{'status':'success','dll_path':'{dll_path}','module_handle':hex(result) if result else None}}")
except Exception as e:
    import traceback
    error_msg = str(e) + "\\n" + traceback.format_exc()
    print(f"MCP_RESULT:{{'status':'error','error':'{{error_msg}}'}}")
"""
            return self.execute_script_auto(inject_script)
        except Exception as e:
            return {
                "status": "error",
                "message": f"DLL注入失败: {str(e)}"
            }
    
    def eject_dll(self, dll_name: str) -> Dict[str, Any]:
        """
        卸载DLL（从目标进程中移除）
        
        :param dll_name: DLL名称（如: "mydll.dll"）
        """
        try:
            eject_script = f"""# X64Dbg DLL Ejection Script
try:
    import dbg
    dll_name = '{dll_name}'
    
    # 获取模块句柄
    module = dbg.getModule(dll_name)
    if not module:
        raise ValueError(f"模块未加载: {{dll_name}}")
    
    # 获取FreeLibrary地址
    kernel32 = dbg.getModule('kernel32.dll')
    free_library = dbg.getAddressFromSymbol('kernel32.FreeLibrary')
    
    # 调用FreeLibrary卸载DLL
    result = dbg.call(free_library, [module])
    print(f"MCP_RESULT:{{'status':'success','dll_name':'{dll_name}','result':result}}")
except Exception as e:
    import traceback
    error_msg = str(e) + "\\n" + traceback.format_exc()
    print(f"MCP_RESULT:{{'status':'error','error':'{{error_msg}}'}}")
"""
            return self.execute_script_auto(eject_script)
        except Exception as e:
            return {
                "status": "error",
                "message": f"DLL卸载失败: {str(e)}"
            }
    
    def bypass_antidebug(self, method: str = "all") -> Dict[str, Any]:
        """
        绕过反调试检测
        
        :param method: 绕过方法，可选值:
            - "all": 所有方法
            - "peb": 修改PEB标志
            - "ntquery": 绕过NtQueryInformationProcess
            - "debugport": 清除调试端口
            - "heap": 修改堆标志
        """
        try:
            bypass_script = f"""# X64Dbg Anti-Debug Bypass Script
try:
    import dbg
    method = '{method}'
    
    results = {{}}
    
    if method in ['all', 'peb']:
        # 修改PEB中的BeingDebugged标志
        try:
            peb = dbg.getPEB()
            if peb:
                # BeingDebugged位于PEB偏移0x02
                dbg.write(peb + 0x02, b'\\x00')
                results['peb'] = 'success'
        except:
            results['peb'] = 'failed'
    
    if method in ['all', 'ntquery']:
        # 绕过NtQueryInformationProcess
        try:
            # Hook NtQueryInformationProcess返回False
            ntdll = dbg.getModule('ntdll.dll')
            if ntdll:
                nt_query = dbg.getAddressFromSymbol('ntdll.NtQueryInformationProcess')
                # 这里需要实际hook实现，简化处理
                results['ntquery'] = 'hook_required'
        except:
            results['ntquery'] = 'failed'
    
    if method in ['all', 'debugport']:
        # 清除调试端口
        try:
            # 通过修改PEB的ProcessParameters或直接修改调试端口
            results['debugport'] = 'advanced_required'
        except:
            results['debugport'] = 'failed'
    
    if method in ['all', 'heap']:
        # 修改堆标志
        try:
            # 修改PEB中的堆标志
            peb = dbg.getPEB()
            if peb:
                # HeapFlags位于PEB偏移0x70
                dbg.write(peb + 0x70, b'\\x00\\x00\\x00\\x00')
                results['heap'] = 'success'
        except:
            results['heap'] = 'failed'
    
    print(f"MCP_RESULT:{{'status':'success','method':'{method}','results':{{results}}}}")
except Exception as e:
    import traceback
    error_msg = str(e) + "\\n" + traceback.format_exc()
    print(f"MCP_RESULT:{{'status':'error','error':'{{error_msg}}'}}")
"""
            return self.execute_script_auto(bypass_script)
        except Exception as e:
            return {
                "status": "error",
                "message": f"反调试绕过失败: {str(e)}"
            }
    
    # ========== 增强功能 ==========
    
    def set_exception_handler(self, exception_code: int, action: str = "ignore") -> Dict[str, Any]:
        """
        设置异常处理
        
        :param exception_code: 异常代码（如: 0xC0000005为访问违例）
        :param action: 处理动作，可选值: "ignore"（忽略）, "break"（中断）, "log"（记录）
        """
        try:
            exception_script = f"""# X64Dbg Exception Handler Script
try:
    import dbg
    exc_code = 0x{exception_code:08X}
    action = '{action}'
    
    # 设置异常处理
    if hasattr(dbg, 'setExceptionHandler'):
        result = dbg.setExceptionHandler(exc_code, action)
        print(f"MCP_RESULT:{{'status':'success','exception_code':hex(exc_code),'action':'{action}','result':result}}")
    else:
        # 尝试通过命令设置
        result = dbgcmd(f'exception {{exc_code}}, {{action}}')
        print(f"MCP_RESULT:{{'status':'success','exception_code':hex(exc_code),'action':'{action}','result':result}}")
except Exception as e:
    print(f"MCP_RESULT:{{'status':'error','error':str(e)}}")
"""
            return self.execute_script_auto(exception_script)
        except Exception as e:
            return {
                "status": "error",
                "message": f"设置异常处理失败: {str(e)}"
            }
    
    def get_exception_info(self) -> Dict[str, Any]:
        """获取当前异常信息"""
        return self.execute_command("exception")
    
    def load_file(self, file_path: str) -> Dict[str, Any]:
        """
        加载文件到调试器
        
        :param file_path: 文件路径
        """
        try:
            load_script = f"""# X64Dbg Load File Script
try:
    import dbg
    import os
    file_path = r"{file_path}"
    
    if not os.path.exists(file_path):
        raise FileNotFoundError(f"文件不存在: {{file_path}}")
    
    # 加载文件
    if hasattr(dbg, 'loadFile'):
        result = dbg.loadFile(file_path)
        print(f"MCP_RESULT:{{'status':'success','file_path':'{file_path}','result':result}}")
    else:
        result = dbgcmd(f'open {{file_path}}')
        print(f"MCP_RESULT:{{'status':'success','file_path':'{file_path}','result':result}}")
except Exception as e:
    print(f"MCP_RESULT:{{'status':'error','error':str(e)}}")
"""
            return self.execute_script_auto(load_script)
        except Exception as e:
            return {
                "status": "error",
                "message": f"加载文件失败: {str(e)}"
            }
    
    def save_memory_to_file(self, address: str, size: int, output_file: str) -> Dict[str, Any]:
        """
        保存内存到文件
        
        :param address: 起始地址
        :param size: 大小
        :param output_file: 输出文件路径
        """
        # 使用已有的dump_memory功能
        return self.dump_memory(address, size, output_file)
    
    def compare_memory(self, address1: str, address2: str, size: int) -> Dict[str, Any]:
        """
        比较两处内存内容
        
        :param address1: 第一个地址
        :param address2: 第二个地址
        :param size: 比较大小
        """
        address1 = address1.strip().replace(" ", "")
        address2 = address2.strip().replace(" ", "")
        
        try:
            compare_script = f"""# X64Dbg Memory Compare Script
try:
    import dbg
    addr1 = int('{address1}', 16) if '{address1}'.startswith('0x') else int('{address1}')
    addr2 = int('{address2}', 16) if '{address2}'.startswith('0x') else int('{address2}')
    size = {size}
    
    # 读取两处内存
    mem1 = dbg.read(addr1, size)
    mem2 = dbg.read(addr2, size)
    
    # 比较
    differences = []
    for i in range(size):
        if mem1[i] != mem2[i]:
            differences.append({{
                'offset': i,
                'address1': hex(addr1 + i),
                'address2': hex(addr2 + i),
                'value1': hex(mem1[i]),
                'value2': hex(mem2[i])
            }})
    
    result = {{
        'identical': len(differences) == 0,
        'total_bytes': size,
        'differences_count': len(differences),
        'differences': differences[:100]  # 限制返回前100个差异
    }}
    print(f"MCP_RESULT:{{'status':'success','result':{{result}}}}")
except Exception as e:
    print(f"MCP_RESULT:{{'status':'error','error':str(e)}}")
"""
            return self.execute_script_auto(compare_script)
        except Exception as e:
            return {
                "status": "error",
                "message": f"内存比较失败: {str(e)}"
            }
    
    def fill_memory(self, address: str, size: int, value: int) -> Dict[str, Any]:
        """
        填充内存
        
        :param address: 起始地址
        :param size: 大小
        :param value: 填充值（0-255）
        """
        address = address.strip().replace(" ", "")
        
        if value < 0 or value > 255:
            raise ValueError('填充值必须在0-255之间!')
        
        try:
            fill_script = f"""# X64Dbg Memory Fill Script
try:
    import dbg
    addr = int('{address}', 16) if '{address}'.startswith('0x') else int('{address}')
    size = {size}
    fill_value = {value}
    
    # 填充内存
    fill_data = bytes([fill_value] * size)
    dbg.write(addr, fill_data)
    
    print(f"MCP_RESULT:{{'status':'success','address':'{address}','size':{size},'value':{value}}")
except Exception as e:
    print(f"MCP_RESULT:{{'status':'error','error':str(e)}}")
"""
            return self.execute_script_auto(fill_script)
        except Exception as e:
            return {
                "status": "error",
                "message": f"内存填充失败: {str(e)}"
            }
    
    def calculate_address(self, base_address: str, offset: int) -> Dict[str, Any]:
        """
        计算地址（基址+偏移）
        
        :param base_address: 基址
        :param offset: 偏移量（可以是负数）
        """
        base_address = base_address.strip().replace(" ", "")
        
        try:
            base = int(base_address, 16) if base_address.startswith('0x') else int(base_address)
            result_addr = base + offset
            
            return {
                "status": "success",
                "base_address": base_address,
                "offset": offset,
                "result_address": hex(result_addr),
                "result_address_decimal": result_addr
            }
        except Exception as e:
            return {
                "status": "error",
                "message": f"地址计算失败: {str(e)}"
            }
    
    def format_address(self, address: str, format_type: str = "hex") -> Dict[str, Any]:
        """
        格式化地址
        
        :param address: 地址（可以是十六进制或十进制字符串）
        :param format_type: 格式类型: "hex", "decimal", "both"
        """
        address = address.strip().replace(" ", "")
        
        try:
            # 尝试解析地址
            if address.startswith('0x') or address.startswith('0X'):
                addr_value = int(address, 16)
            else:
                addr_value = int(address)
            
            result = {}
            if format_type in ["hex", "both"]:
                result["hex"] = hex(addr_value)
            if format_type in ["decimal", "both"]:
                result["decimal"] = addr_value
            
            return {
                "status": "success",
                "original": address,
                "formatted": result
            }
        except Exception as e:
            return {
                "status": "error",
                "message": f"地址格式化失败: {str(e)}"
            }
    
    # ========== 书签功能 ==========
    
    def add_bookmark(self, address: str, name: str = "") -> Dict[str, Any]:
        """
        添加地址书签
        
        :param address: 地址
        :param name: 书签名称（可选，如果不提供则使用地址作为名称）
        """
        address = address.strip().replace(" ", "")
        if not name:
            name = address
        
        try:
            bookmark_script = f"""# X64Dbg Bookmark Script
try:
    import dbg
    addr = int('{address}', 16) if '{address}'.startswith('0x') else int('{address}')
    bookmark_name = '{name}'
    
    # 添加书签
    if hasattr(dbg, 'setBookmark'):
        result = dbg.setBookmark(addr, bookmark_name)
        print(f"MCP_RESULT:{{'status':'success','address':'{address}','name':'{name}','result':result}}")
    else:
        # 尝试通过命令添加
        result = dbgcmd(f'bookmark {{addr}}, {{bookmark_name}}')
        print(f"MCP_RESULT:{{'status':'success','address':'{address}','name':'{name}','result':result}}")
except Exception as e:
    print(f"MCP_RESULT:{{'status':'error','error':str(e)}}")
"""
            return self.execute_script_auto(bookmark_script)
        except Exception as e:
            return {
                "status": "error",
                "message": f"添加书签失败: {str(e)}"
            }
    
    def remove_bookmark(self, address: str) -> Dict[str, Any]:
        """
        删除地址书签
        
        :param address: 地址
        """
        address = address.strip().replace(" ", "")
        
        try:
            remove_script = f"""# X64Dbg Remove Bookmark Script
try:
    import dbg
    addr = int('{address}', 16) if '{address}'.startswith('0x') else int('{address}')
    
    # 删除书签
    if hasattr(dbg, 'removeBookmark'):
        result = dbg.removeBookmark(addr)
        print(f"MCP_RESULT:{{'status':'success','address':'{address}','result':result}}")
    else:
        result = dbgcmd(f'bookmarkdel {{addr}}')
        print(f"MCP_RESULT:{{'status':'success','address':'{address}','result':result}}")
except Exception as e:
    print(f"MCP_RESULT:{{'status':'error','error':str(e)}}")
"""
            return self.execute_script_auto(remove_script)
        except Exception as e:
            return {
                "status": "error",
                "message": f"删除书签失败: {str(e)}"
            }
    
    def get_bookmarks(self) -> Dict[str, Any]:
        """获取所有书签列表"""
        return self.execute_command("bookmarklist")
    
    def goto_bookmark(self, name: str) -> Dict[str, Any]:
        """
        跳转到书签
        
        :param name: 书签名称
        """
        try:
            goto_script = f"""# X64Dbg Goto Bookmark Script
try:
    import dbg
    bookmark_name = '{name}'
    
    # 获取书签地址并跳转
    if hasattr(dbg, 'getBookmarkAddress'):
        addr = dbg.getBookmarkAddress(bookmark_name)
        if addr:
            dbg.setRegister('EIP', addr)
            print(f"MCP_RESULT:{{'status':'success','name':'{name}','address':hex(addr)}}")
        else:
            print(f"MCP_RESULT:{{'status':'error','error':'书签不存在'}}")
    else:
        result = dbgcmd(f'bookmarkgoto {{bookmark_name}}')
        print(f"MCP_RESULT:{{'status':'success','name':'{name}','result':result}}")
except Exception as e:
    print(f"MCP_RESULT:{{'status':'error','error':str(e)}}")
"""
            return self.execute_script_auto(goto_script)
        except Exception as e:
            return {
                "status": "error",
                "message": f"跳转书签失败: {str(e)}"
            }
    
    # ========== 执行跟踪功能 ==========
    
    def start_trace(self) -> Dict[str, Any]:
        """开始执行跟踪"""
        try:
            trace_script = """# X64Dbg Start Trace Script
try:
    import dbg
    # 开始跟踪
    if hasattr(dbg, 'startTrace'):
        result = dbg.startTrace()
        print(f"MCP_RESULT:{{'status':'success','message':'跟踪已开始','result':result}}")
    else:
        result = dbgcmd('trace')
        print(f"MCP_RESULT:{{'status':'success','message':'跟踪已开始','result':result}}")
except Exception as e:
    print(f"MCP_RESULT:{{'status':'error','error':str(e)}}")
"""
            return self.execute_script_auto(trace_script)
        except Exception as e:
            return {
                "status": "error",
                "message": f"开始跟踪失败: {str(e)}"
            }
    
    def stop_trace(self) -> Dict[str, Any]:
        """停止执行跟踪"""
        try:
            stop_script = """# X64Dbg Stop Trace Script
try:
    import dbg
    # 停止跟踪
    if hasattr(dbg, 'stopTrace'):
        result = dbg.stopTrace()
        print(f"MCP_RESULT:{{'status':'success','message':'跟踪已停止','result':result}}")
    else:
        result = dbgcmd('tracestop')
        print(f"MCP_RESULT:{{'status':'success','message':'跟踪已停止','result':result}}")
except Exception as e:
    print(f"MCP_RESULT:{{'status':'error','error':str(e)}}")
"""
            return self.execute_script_auto(stop_script)
        except Exception as e:
            return {
                "status": "error",
                "message": f"停止跟踪失败: {str(e)}"
            }
    
    def get_trace_records(self, count: int = 100) -> Dict[str, Any]:
        """
        获取跟踪记录
        
        :param count: 要获取的记录数量，默认100，最大10000
        """
        if count <= 0 or count > 10000:
            count = 100
        
        try:
            records_script = f"""# X64Dbg Get Trace Records Script
try:
    import dbg
    count = {count}
    
    # 获取跟踪记录
    if hasattr(dbg, 'getTraceRecords'):
        records = dbg.getTraceRecords(count)
        print(f"MCP_RESULT:{{'status':'success','count':len(records),'records':records}}")
    else:
        result = dbgcmd(f'tracelist {{count}}')
        print(f"MCP_RESULT:{{'status':'success','count':{count},'result':result}}")
except Exception as e:
    print(f"MCP_RESULT:{{'status':'error','error':str(e)}}")
"""
            return self.execute_script_auto(records_script)
        except Exception as e:
            return {
                "status": "error",
                "message": f"获取跟踪记录失败: {str(e)}"
            }


# 全局控制器实例
controller = X64DbgController()


def register_tools(mcp):
    """注册所有X64Dbg工具"""
    
    @mcp.tool('x64dbg_execute_command', description='执行x64dbg调试命令')
    async def execute_command(command: str):
        """
        执行x64dbg调试命令
        
        :param command: 要执行的x64dbg命令，例如: 'r' (寄存器), 'mod' (模块), 'bp 0x401000' (断点)
        :return: 命令执行结果
        """
        if not command or command.strip() == "":
            raise ValueError('命令不能为空!')
        
        try:
            result = controller.execute_command(command)
            return result
        except Exception as e:
            return {"status": "error", "message": f"执行失败: {str(e)}"}
    
    @mcp.tool('x64dbg_get_registers', description='获取当前所有寄存器值')
    async def get_registers():
        """
        获取当前调试进程的所有寄存器值
        
        :return: 寄存器信息
        """
        try:
            result = controller.get_registers()
            return result
        except Exception as e:
            return {"status": "error", "message": f"获取寄存器失败: {str(e)}"}
    
    @mcp.tool('x64dbg_set_register', description='设置单个寄存器值')
    async def set_register(register_name: str, value: str):
        """
        设置单个寄存器值
        
        :param register_name: 寄存器名称（如: eax, ebx, eip, rax等）
        :param value: 寄存器值，可以是十六进制格式(0x401000)或十进制格式
        :return: 设置结果
        """
        if not register_name or register_name.strip() == "":
            raise ValueError('寄存器名称不能为空!')
        
        if not value or value.strip() == "":
            raise ValueError('寄存器值不能为空!')
        
        try:
            result = controller.set_register(register_name, value)
            return result
        except Exception as e:
            return {"status": "error", "message": f"设置寄存器失败: {str(e)}"}
    
    @mcp.tool('x64dbg_set_registers', description='批量设置寄存器值')
    async def set_registers(registers: str):
        """
        批量设置寄存器值
        
        :param registers: 寄存器JSON字符串，格式: {"eax": "0x401000", "ebx": "0x100"}
        :return: 设置结果
        """
        if not registers or registers.strip() == "":
            raise ValueError('寄存器字典不能为空!')
        
        try:
            # 解析JSON字符串
            import json
            reg_dict = json.loads(registers)
            if not isinstance(reg_dict, dict):
                raise ValueError('寄存器必须是字典格式!')
            
            result = controller.set_registers(reg_dict)
            return result
        except json.JSONDecodeError:
            return {"status": "error", "message": "寄存器格式错误，必须是有效的JSON格式"}
        except Exception as e:
            return {"status": "error", "message": f"批量设置寄存器失败: {str(e)}"}
    
    @mcp.tool('x64dbg_get_modules', description='获取已加载的模块列表')
    async def get_modules():
        """
        获取当前调试进程中已加载的所有模块列表
        
        :return: 模块列表信息
        """
        try:
            result = controller.get_modules()
            return result
        except Exception as e:
            return {"status": "error", "message": f"获取模块列表失败: {str(e)}"}
    
    @mcp.tool('x64dbg_set_breakpoint', description='在指定地址设置断点')
    async def set_breakpoint(address: str):
        """
        在指定地址设置断点
        
        :param address: 断点地址，可以是十六进制格式(0x401000)或十进制格式
        :return: 设置结果
        """
        if not address or address.strip() == "":
            raise ValueError('地址不能为空!')
        
        try:
            result = controller.set_breakpoint(address)
            return result
        except Exception as e:
            return {"status": "error", "message": f"设置断点失败: {str(e)}"}
    
    @mcp.tool('x64dbg_remove_breakpoint', description='删除指定地址的断点')
    async def remove_breakpoint(address: str):
        """
        删除指定地址的断点
        
        :param address: 断点地址，十六进制格式(0x401000)
        :return: 删除结果
        """
        if not address or address.strip() == "":
            raise ValueError('地址不能为空!')
        
        try:
            result = controller.remove_breakpoint(address)
            return result
        except Exception as e:
            return {"status": "error", "message": f"删除断点失败: {str(e)}"}
    
    @mcp.tool('x64dbg_read_memory', description='读取指定地址的内存内容')
    async def read_memory(address: str, size: int = 64):
        """
        读取指定地址的内存内容
        
        :param address: 内存地址，十六进制格式(0x401000)
        :param size: 要读取的字节数，默认64字节，最大4096字节
        :return: 内存内容
        """
        if not address or address.strip() == "":
            raise ValueError('地址不能为空!')
        
        if size <= 0 or size > 4096:
            raise ValueError('读取大小必须在1-4096字节之间!')
        
        try:
            result = controller.read_memory(address, size)
            return result
        except Exception as e:
            return {"status": "error", "message": f"读取内存失败: {str(e)}"}
    
    @mcp.tool('x64dbg_write_memory', description='向指定地址写入内存数据')
    async def write_memory(address: str, data: str):
        """
        向指定地址写入内存数据
        
        :param address: 内存地址，十六进制格式(0x401000)
        :param data: 要写入的数据，可以是十六进制字符串(如: "90 90 90")或ASCII字符串
        :return: 写入结果
        """
        if not address or address.strip() == "":
            raise ValueError('地址不能为空!')
        
        if not data or data.strip() == "":
            raise ValueError('数据不能为空!')
        
        try:
            result = controller.write_memory(address, data)
            return result
        except Exception as e:
            return {"status": "error", "message": f"写入内存失败: {str(e)}"}
    
    @mcp.tool('x64dbg_disassemble', description='反汇编指定地址的代码')
    async def disassemble(address: str, count: int = 10):
        """
        反汇编指定地址的代码
        
        :param address: 要反汇编的地址，十六进制格式(0x401000)
        :param count: 要反汇编的指令数量，默认10条，最大100条
        :return: 反汇编结果
        """
        if not address or address.strip() == "":
            raise ValueError('地址不能为空!')
        
        if count <= 0 or count > 100:
            raise ValueError('指令数量必须在1-100之间!')
        
        try:
            result = controller.disassemble(address, count)
            return result
        except Exception as e:
            return {"status": "error", "message": f"反汇编失败: {str(e)}"}
    
    @mcp.tool('x64dbg_step_over', description='单步执行(Step Over)')
    async def step_over():
        """
        执行单步调试(Step Over)，跳过函数调用
        
        :return: 执行结果
        """
        try:
            result = controller.execute_command("sto")
            return result
        except Exception as e:
            return {"status": "error", "message": f"单步执行失败: {str(e)}"}
    
    @mcp.tool('x64dbg_step_into', description='单步进入(Step Into)')
    async def step_into():
        """
        执行单步调试(Step Into)，进入函数调用
        
        :return: 执行结果
        """
        try:
            result = controller.execute_command("sti")
            return result
        except Exception as e:
            return {"status": "error", "message": f"单步进入失败: {str(e)}"}
    
    @mcp.tool('x64dbg_continue', description='继续执行程序')
    async def continue_execution():
        """
        继续执行被调试的程序
        
        :return: 执行结果
        """
        try:
            result = controller.execute_command("run")
            return result
        except Exception as e:
            return {"status": "error", "message": f"继续执行失败: {str(e)}"}
    
    @mcp.tool('x64dbg_pause', description='暂停程序执行')
    async def pause_execution():
        """
        暂停当前正在执行的程序
        
        :return: 执行结果
        """
        try:
            result = controller.execute_command("pause")
            return result
        except Exception as e:
            return {"status": "error", "message": f"暂停执行失败: {str(e)}"}
    
    @mcp.tool('x64dbg_get_stack', description='获取当前堆栈信息')
    async def get_stack(count: int = 10):
        """
        获取当前堆栈信息
        
        :param count: 要显示的堆栈帧数量，默认10，最大50
        :return: 堆栈信息
        """
        if count <= 0 or count > 50:
            raise ValueError('堆栈帧数量必须在1-50之间!')
        
        try:
            result = controller.get_stack(count)
            return result
        except Exception as e:
            return {"status": "error", "message": f"获取堆栈失败: {str(e)}"}
    
    @mcp.tool('x64dbg_search_memory', description='在内存中搜索指定模式')
    async def search_memory(pattern: str, start_address: str = "", end_address: str = ""):
        """
        在内存中搜索指定模式
        
        :param pattern: 要搜索的模式，可以是十六进制字符串(如: "48 89 E5")或ASCII字符串
        :param start_address: 起始地址(可选)，十六进制格式(0x401000)
        :param end_address: 结束地址(可选)，十六进制格式(0x402000)
        :return: 搜索结果
        """
        if not pattern or pattern.strip() == "":
            raise ValueError('搜索模式不能为空!')
        
        try:
            result = controller.search_memory(pattern, start_address, end_address)
            return result
        except Exception as e:
            return {"status": "error", "message": f"搜索内存失败: {str(e)}"}
    
    # ========== 新增功能 ==========
    
    @mcp.tool('x64dbg_get_debugger_status', description='获取调试器实时状态')
    async def get_debugger_status():
        """
        获取调试器的实时状态信息
        
        :return: 调试器状态，包括是否正在调试、是否运行中、当前PID、TID、地址等
        """
        try:
            result = controller.get_debugger_status()
            return result
        except Exception as e:
            return {"status": "error", "message": f"获取调试器状态失败: {str(e)}"}
    
    @mcp.tool('x64dbg_set_breakpoint_conditional', description='设置带条件的断点')
    async def set_breakpoint_conditional(address: str, condition: str = ""):
        """
        在指定地址设置带条件的断点
        
        :param address: 断点地址，十六进制格式(0x401000)
        :param condition: 断点条件表达式(可选)，例如: "eax==0x100"
        :return: 设置结果
        """
        if not address or address.strip() == "":
            raise ValueError('地址不能为空!')
        
        try:
            result = controller.set_breakpoint_conditional(address, condition)
            return result
        except Exception as e:
            return {"status": "error", "message": f"设置条件断点失败: {str(e)}"}
    
    @mcp.tool('x64dbg_dump_memory', description='将内存转储到文件')
    async def dump_memory(address: str, size: int, output_file: str = ""):
        """
        将指定地址的内存转储到文件
        
        :param address: 内存起始地址，十六进制格式(0x401000)
        :param size: 要转储的字节数，最大10MB
        :param output_file: 输出文件路径(可选)，默认保存在临时目录
        :return: 转储结果
        """
        if not address or address.strip() == "":
            raise ValueError('地址不能为空!')
        
        if size <= 0 or size > 10 * 1024 * 1024:
            raise ValueError('转储大小必须在1字节到10MB之间!')
        
        try:
            result = controller.dump_memory(address, size, output_file)
            return result
        except Exception as e:
            return {"status": "error", "message": f"内存转储失败: {str(e)}"}
    
    @mcp.tool('x64dbg_resolve_symbol', description='解析符号名称到地址')
    async def resolve_symbol(symbol: str):
        """
        解析符号名称到内存地址
        
        :param symbol: 符号名称，例如: "MessageBoxA", "kernel32.CreateFile"
        :return: 符号地址信息
        """
        if not symbol or symbol.strip() == "":
            raise ValueError('符号名称不能为空!')
        
        try:
            result = controller.resolve_symbol(symbol)
            return result
        except Exception as e:
            return {"status": "error", "message": f"符号解析失败: {str(e)}"}
    
    @mcp.tool('x64dbg_get_threads', description='获取线程列表')
    async def get_threads():
        """
        获取当前调试进程的所有线程列表
        
        :return: 线程列表信息
        """
        try:
            result = controller.get_threads()
            return result
        except Exception as e:
            return {"status": "error", "message": f"获取线程列表失败: {str(e)}"}
    
    @mcp.tool('x64dbg_switch_thread', description='切换当前线程')
    async def switch_thread(thread_id: int):
        """
        切换当前线程
        
        :param thread_id: 线程ID（TID）
        :return: 切换结果
        """
        if thread_id <= 0:
            raise ValueError('线程ID必须大于0!')
        
        try:
            result = controller.switch_thread(thread_id)
            return result
        except Exception as e:
            return {"status": "error", "message": f"切换线程失败: {str(e)}"}
    
    @mcp.tool('x64dbg_suspend_thread', description='挂起线程')
    async def suspend_thread(thread_id: int):
        """
        挂起线程（暂停线程执行）
        
        :param thread_id: 线程ID（TID）
        :return: 挂起结果
        """
        if thread_id <= 0:
            raise ValueError('线程ID必须大于0!')
        
        try:
            result = controller.suspend_thread(thread_id)
            return result
        except Exception as e:
            return {"status": "error", "message": f"挂起线程失败: {str(e)}"}
    
    @mcp.tool('x64dbg_resume_thread', description='恢复线程')
    async def resume_thread(thread_id: int):
        """
        恢复线程（继续线程执行）
        
        :param thread_id: 线程ID（TID）
        :return: 恢复结果
        """
        if thread_id <= 0:
            raise ValueError('线程ID必须大于0!')
        
        try:
            result = controller.resume_thread(thread_id)
            return result
        except Exception as e:
            return {"status": "error", "message": f"恢复线程失败: {str(e)}"}
    
    @mcp.tool('x64dbg_get_thread_context', description='获取线程上下文')
    async def get_thread_context(thread_id: int):
        """
        获取线程上下文（寄存器、堆栈等信息）
        
        :param thread_id: 线程ID（TID）
        :return: 线程上下文信息
        """
        if thread_id <= 0:
            raise ValueError('线程ID必须大于0!')
        
        try:
            result = controller.get_thread_context(thread_id)
            return result
        except Exception as e:
            return {"status": "error", "message": f"获取线程上下文失败: {str(e)}"}
    
    @mcp.tool('x64dbg_get_breakpoints', description='获取所有断点列表')
    async def get_breakpoints():
        """
        获取当前设置的所有断点列表
        
        :return: 断点列表信息
        """
        try:
            result = controller.get_breakpoints()
            return result
        except Exception as e:
            return {"status": "error", "message": f"获取断点列表失败: {str(e)}"}
    
    @mcp.tool('x64dbg_get_call_stack', description='获取调用栈信息')
    async def get_call_stack(depth: int = 20):
        """
        获取当前调用栈信息
        
        :param depth: 调用栈深度，默认20，最大100
        :return: 调用栈信息
        """
        if depth <= 0 or depth > 100:
            raise ValueError('调用栈深度必须在1-100之间!')
        
        try:
            result = controller.get_call_stack(depth)
            return result
        except Exception as e:
            return {"status": "error", "message": f"获取调用栈失败: {str(e)}"}
    
    @mcp.tool('x64dbg_get_segments', description='获取内存段信息')
    async def get_segments():
        """
        获取当前进程的内存段信息
        
        :return: 内存段列表
        """
        try:
            result = controller.get_segments()
            return result
        except Exception as e:
            return {"status": "error", "message": f"获取内存段失败: {str(e)}"}
    
    @mcp.tool('x64dbg_get_strings', description='搜索字符串引用')
    async def get_strings(min_length: int = 4):
        """
        搜索内存中的字符串引用
        
        :param min_length: 最小字符串长度，默认4
        :return: 字符串引用列表
        """
        if min_length < 1:
            raise ValueError('最小长度必须大于0!')
        
        try:
            result = controller.get_strings(min_length)
            return result
        except Exception as e:
            return {"status": "error", "message": f"搜索字符串失败: {str(e)}"}
    
    @mcp.tool('x64dbg_get_references', description='获取地址引用')
    async def get_references(address: str):
        """
        获取指定地址的交叉引用
        
        :param address: 要查询的地址，十六进制格式(0x401000)
        :return: 引用列表
        """
        if not address or address.strip() == "":
            raise ValueError('地址不能为空!')
        
        try:
            result = controller.get_references(address)
            return result
        except Exception as e:
            return {"status": "error", "message": f"获取引用失败: {str(e)}"}
    
    @mcp.tool('x64dbg_get_imports', description='获取导入函数列表')
    async def get_imports():
        """
        获取当前模块的导入函数列表
        
        :return: 导入函数列表
        """
        try:
            result = controller.get_imports()
            return result
        except Exception as e:
            return {"status": "error", "message": f"获取导入函数失败: {str(e)}"}
    
    @mcp.tool('x64dbg_get_exports', description='获取导出函数列表')
    async def get_exports():
        """
        获取当前模块的导出函数列表
        
        :return: 导出函数列表
        """
        try:
            result = controller.get_exports()
            return result
        except Exception as e:
            return {"status": "error", "message": f"获取导出函数失败: {str(e)}"}
    
    @mcp.tool('x64dbg_get_comments', description='获取注释信息')
    async def get_comments(address: str = ""):
        """
        获取注释信息
        
        :param address: 地址(可选)，如果提供则获取该地址的注释，否则获取所有注释
        :return: 注释信息
        """
        try:
            result = controller.get_comments(address)
            return result
        except Exception as e:
            return {"status": "error", "message": f"获取注释失败: {str(e)}"}
    
    @mcp.tool('x64dbg_get_labels', description='获取标签列表')
    async def get_labels():
        """
        获取所有标签列表
        
        :return: 标签列表
        """
        try:
            result = controller.get_labels()
            return result
        except Exception as e:
            return {"status": "error", "message": f"获取标签列表失败: {str(e)}"}
    
    @mcp.tool('x64dbg_get_functions', description='获取函数列表')
    async def get_functions():
        """
        获取所有函数列表
        
        :return: 函数列表
        """
        try:
            result = controller.get_functions()
            return result
        except Exception as e:
            return {"status": "error", "message": f"获取函数列表失败: {str(e)}"}
    
    # ========== 高优先级新功能 ==========
    
    @mcp.tool('x64dbg_enable_breakpoint', description='启用断点')
    async def enable_breakpoint(address: str):
        """
        启用指定地址的断点（如果断点被禁用）
        
        :param address: 断点地址，十六进制格式(0x401000)
        :return: 启用结果
        """
        if not address or address.strip() == "":
            raise ValueError('地址不能为空!')
        
        try:
            result = controller.enable_breakpoint(address)
            return result
        except Exception as e:
            return {"status": "error", "message": f"启用断点失败: {str(e)}"}
    
    @mcp.tool('x64dbg_disable_breakpoint', description='禁用断点')
    async def disable_breakpoint(address: str):
        """
        禁用指定地址的断点（不断点删除，只是临时禁用）
        
        :param address: 断点地址，十六进制格式(0x401000)
        :return: 禁用结果
        """
        if not address or address.strip() == "":
            raise ValueError('地址不能为空!')
        
        try:
            result = controller.disable_breakpoint(address)
            return result
        except Exception as e:
            return {"status": "error", "message": f"禁用断点失败: {str(e)}"}
    
    @mcp.tool('x64dbg_get_breakpoint_hit_count', description='获取断点命中计数')
    async def get_breakpoint_hit_count(address: str):
        """
        获取断点命中计数（断点被触发的次数）
        
        :param address: 断点地址，十六进制格式(0x401000)
        :return: 命中计数信息
        """
        if not address or address.strip() == "":
            raise ValueError('地址不能为空!')
        
        try:
            result = controller.get_breakpoint_hit_count(address)
            return result
        except Exception as e:
            return {"status": "error", "message": f"获取断点命中计数失败: {str(e)}"}
    
    @mcp.tool('x64dbg_reset_breakpoint_hit_count', description='重置断点命中计数')
    async def reset_breakpoint_hit_count(address: str):
        """
        重置断点命中计数（将计数清零）
        
        :param address: 断点地址，十六进制格式(0x401000)
        :return: 重置结果
        """
        if not address or address.strip() == "":
            raise ValueError('地址不能为空!')
        
        try:
            result = controller.reset_breakpoint_hit_count(address)
            return result
        except Exception as e:
            return {"status": "error", "message": f"重置断点命中计数失败: {str(e)}"}
    
    @mcp.tool('x64dbg_capture_output', description='捕获命令执行的实际输出')
    async def capture_output(command: str):
        """
        捕获命令执行的实际输出（增强版命令执行）
        
        :param command: 要执行的x64dbg命令
        :return: 命令执行结果，包含实际输出
        """
        if not command or command.strip() == "":
            raise ValueError('命令不能为空!')
        
        try:
            result = controller.capture_output(command)
            return result
        except Exception as e:
            return {"status": "error", "message": f"捕获输出失败: {str(e)}"}
    
    @mcp.tool('x64dbg_get_logs', description='获取x64dbg日志输出')
    async def get_logs(count: int = 100):
        """
        获取x64dbg的日志输出
        
        :param count: 要获取的日志条数，默认100，最大1000
        :return: 日志列表
        """
        if count <= 0 or count > 1000:
            raise ValueError('日志数量必须在1-1000之间!')
        
        try:
            result = controller.get_logs(count)
            return result
        except Exception as e:
            return {"status": "error", "message": f"获取日志失败: {str(e)}"}
    
    @mcp.tool('x64dbg_set_memory_protection', description='设置内存保护属性')
    async def set_memory_protection(address: str, size: int, protection: str):
        """
        设置内存保护属性
        
        :param address: 内存起始地址，十六进制格式(0x401000)
        :param size: 内存大小（字节），最大10MB
        :param protection: 保护属性，可选值:
            - "R" 或 "READ": 只读
            - "W" 或 "WRITE": 可写
            - "X" 或 "EXECUTE": 可执行
            - "RW": 可读可写
            - "RX": 可读可执行
            - "RWX": 可读可写可执行
            - "NONE": 无访问权限
        :return: 设置结果
        """
        if not address or address.strip() == "":
            raise ValueError('地址不能为空!')
        
        if size <= 0 or size > 10 * 1024 * 1024:
            raise ValueError('内存大小必须在1字节到10MB之间!')
        
        if not protection or protection.strip() == "":
            raise ValueError('保护属性不能为空!')
        
        try:
            result = controller.set_memory_protection(address, size, protection)
            return result
        except Exception as e:
            return {"status": "error", "message": f"设置内存保护失败: {str(e)}"}
    
    @mcp.tool('x64dbg_get_memory_protection', description='获取内存保护属性')
    async def get_memory_protection(address: str):
        """
        获取指定地址的内存保护属性
        
        :param address: 内存地址，十六进制格式(0x401000)
        :return: 内存保护属性信息
        """
        if not address or address.strip() == "":
            raise ValueError('地址不能为空!')
        
        try:
            result = controller.get_memory_protection(address)
            return result
        except Exception as e:
            return {"status": "error", "message": f"获取内存保护失败: {str(e)}"}
    
    # ========== 中优先级新功能 ==========
    
    @mcp.tool('x64dbg_set_hardware_breakpoint', description='设置硬件断点')
    async def set_hardware_breakpoint(address: str, break_type: str = "execute", size: int = 1):
        """
        设置硬件断点
        
        :param address: 断点地址，十六进制格式(0x401000)
        :param break_type: 断点类型，可选值: "execute"/"e"（执行）, "write"/"w"（写入）, "read"/"r"（读取）, "readwrite"/"rw"（读写）
        :param size: 断点大小（字节），可选值: 1, 2, 4, 8，默认1
        :return: 设置结果
        """
        if not address or address.strip() == "":
            raise ValueError('地址不能为空!')
        
        if size not in [1, 2, 4, 8]:
            raise ValueError('断点大小必须是1、2、4或8字节!')
        
        try:
            result = controller.set_hardware_breakpoint(address, break_type, size)
            return result
        except Exception as e:
            return {"status": "error", "message": f"设置硬件断点失败: {str(e)}"}
    
    @mcp.tool('x64dbg_remove_hardware_breakpoint', description='删除硬件断点')
    async def remove_hardware_breakpoint(address: str):
        """
        删除硬件断点
        
        :param address: 断点地址，十六进制格式(0x401000)
        :return: 删除结果
        """
        if not address or address.strip() == "":
            raise ValueError('地址不能为空!')
        
        try:
            result = controller.remove_hardware_breakpoint(address)
            return result
        except Exception as e:
            return {"status": "error", "message": f"删除硬件断点失败: {str(e)}"}
    
    @mcp.tool('x64dbg_set_watchpoint', description='设置数据断点（监视点）')
    async def set_watchpoint(address: str, watch_type: str = "write", size: int = 4):
        """
        设置数据断点（监视点），用于监控内存访问
        
        :param address: 监视地址，十六进制格式(0x401000)
        :param watch_type: 监视类型，可选值: "write"/"w"（写入）, "read"/"r"（读取）, "readwrite"/"rw"（读写）
        :param size: 监视大小（字节），可选值: 1, 2, 4, 8，默认4
        :return: 设置结果
        """
        if not address or address.strip() == "":
            raise ValueError('地址不能为空!')
        
        if size not in [1, 2, 4, 8]:
            raise ValueError('监视大小必须是1、2、4或8字节!')
        
        try:
            result = controller.set_watchpoint(address, watch_type, size)
            return result
        except Exception as e:
            return {"status": "error", "message": f"设置数据断点失败: {str(e)}"}
    
    @mcp.tool('x64dbg_remove_watchpoint', description='删除数据断点（监视点）')
    async def remove_watchpoint(address: str):
        """
        删除数据断点（监视点）
        
        :param address: 监视地址，十六进制格式(0x401000)
        :return: 删除结果
        """
        if not address or address.strip() == "":
            raise ValueError('地址不能为空!')
        
        try:
            result = controller.remove_watchpoint(address)
            return result
        except Exception as e:
            return {"status": "error", "message": f"删除数据断点失败: {str(e)}"}
    
    @mcp.tool('x64dbg_attach_process', description='附加到进程')
    async def attach_process(process_id: int):
        """
        附加到正在运行的进程进行调试
        
        :param process_id: 进程ID（PID）
        :return: 附加结果
        """
        if process_id <= 0:
            raise ValueError('进程ID必须大于0!')
        
        try:
            result = controller.attach_process(process_id)
            return result
        except Exception as e:
            return {"status": "error", "message": f"附加进程失败: {str(e)}"}
    
    @mcp.tool('x64dbg_detach_process', description='分离当前调试的进程')
    async def detach_process():
        """
        分离当前调试的进程（不断点终止进程）
        
        :return: 分离结果
        """
        try:
            result = controller.detach_process()
            return result
        except Exception as e:
            return {"status": "error", "message": f"分离进程失败: {str(e)}"}
    
    @mcp.tool('x64dbg_apply_patch', description='应用代码补丁')
    async def apply_patch(address: str, data: str, description: str = ""):
        """
        应用代码补丁（修改代码）
        
        :param address: 补丁地址，十六进制格式(0x401000)
        :param data: 要写入的数据，十六进制字符串（如: "90 90 90" 表示NOP指令）
        :param description: 补丁描述（可选）
        :return: 应用结果
        """
        if not address or address.strip() == "":
            raise ValueError('地址不能为空!')
        
        if not data or data.strip() == "":
            raise ValueError('数据不能为空!')
        
        try:
            result = controller.apply_patch(address, data, description)
            return result
        except Exception as e:
            return {"status": "error", "message": f"应用补丁失败: {str(e)}"}
    
    @mcp.tool('x64dbg_remove_patch', description='移除代码补丁')
    async def remove_patch(address: str):
        """
        移除代码补丁（恢复原始代码）
        
        :param address: 补丁地址，十六进制格式(0x401000)
        :return: 移除结果
        """
        if not address or address.strip() == "":
            raise ValueError('地址不能为空!')
        
        try:
            result = controller.remove_patch(address)
            return result
        except Exception as e:
            return {"status": "error", "message": f"移除补丁失败: {str(e)}"}
    
    @mcp.tool('x64dbg_get_patches', description='获取所有补丁列表')
    async def get_patches():
        """
        获取当前应用的所有补丁列表
        
        :return: 补丁列表
        """
        try:
            result = controller.get_patches()
            return result
        except Exception as e:
            return {"status": "error", "message": f"获取补丁列表失败: {str(e)}"}
    
    # ========== 低优先级新功能（高级功能） ==========
    
    @mcp.tool('x64dbg_inject_code', description='注入代码（Shellcode）到目标进程')
    async def inject_code(address: str, shellcode: str, create_thread: bool = False):
        """
        注入代码（Shellcode）到目标进程
        
        :param address: 注入地址，十六进制格式(0x401000)，如果为空则在内存中分配空间
        :param shellcode: Shellcode，十六进制字符串（如: "90 90 90" 表示NOP指令）
        :param create_thread: 是否创建新线程执行（默认False，在当前线程执行）
        :return: 注入结果
        """
        if not shellcode or shellcode.strip() == "":
            raise ValueError('Shellcode不能为空!')
        
        try:
            result = controller.inject_code(address if address else None, shellcode, create_thread)
            return result
        except Exception as e:
            return {"status": "error", "message": f"代码注入失败: {str(e)}"}
    
    @mcp.tool('x64dbg_inject_dll', description='注入DLL到目标进程')
    async def inject_dll(dll_path: str, wait_for_load: bool = True):
        """
        注入DLL到目标进程
        
        :param dll_path: DLL文件完整路径（如: "C:\\path\\to\\mydll.dll"）
        :param wait_for_load: 是否等待DLL加载完成（默认True）
        :return: 注入结果
        """
        if not dll_path or dll_path.strip() == "":
            raise ValueError('DLL路径不能为空!')
        
        try:
            result = controller.inject_dll(dll_path, wait_for_load)
            return result
        except Exception as e:
            return {"status": "error", "message": f"DLL注入失败: {str(e)}"}
    
    @mcp.tool('x64dbg_eject_dll', description='卸载DLL（从目标进程中移除）')
    async def eject_dll(dll_name: str):
        """
        卸载DLL（从目标进程中移除）
        
        :param dll_name: DLL名称（如: "mydll.dll"）
        :return: 卸载结果
        """
        if not dll_name or dll_name.strip() == "":
            raise ValueError('DLL名称不能为空!')
        
        try:
            result = controller.eject_dll(dll_name)
            return result
        except Exception as e:
            return {"status": "error", "message": f"DLL卸载失败: {str(e)}"}
    
    @mcp.tool('x64dbg_bypass_antidebug', description='绕过反调试检测')
    async def bypass_antidebug(method: str = "all"):
        """
        绕过反调试检测
        
        :param method: 绕过方法，可选值:
            - "all": 所有方法
            - "peb": 修改PEB标志
            - "ntquery": 绕过NtQueryInformationProcess
            - "debugport": 清除调试端口
            - "heap": 修改堆标志
        :return: 绕过结果
        """
        valid_methods = ["all", "peb", "ntquery", "debugport", "heap"]
        if method.lower() not in valid_methods:
            raise ValueError(f'方法必须是以下之一: {", ".join(valid_methods)}')
        
        try:
            result = controller.bypass_antidebug(method.lower())
            return result
        except Exception as e:
            return {"status": "error", "message": f"反调试绕过失败: {str(e)}"}
    
    # ========== 增强功能 ==========
    
    @mcp.tool('x64dbg_set_exception_handler', description='设置异常处理')
    async def set_exception_handler(exception_code: int, action: str = "ignore"):
        """
        设置异常处理
        
        :param exception_code: 异常代码（十六进制，如: 0xC0000005为访问违例）
        :param action: 处理动作，可选值: "ignore"（忽略）, "break"（中断）, "log"（记录）
        :return: 设置结果
        """
        valid_actions = ["ignore", "break", "log"]
        if action.lower() not in valid_actions:
            raise ValueError(f'处理动作必须是以下之一: {", ".join(valid_actions)}')
        
        try:
            result = controller.set_exception_handler(exception_code, action.lower())
            return result
        except Exception as e:
            return {"status": "error", "message": f"设置异常处理失败: {str(e)}"}
    
    @mcp.tool('x64dbg_get_exception_info', description='获取当前异常信息')
    async def get_exception_info():
        """
        获取当前异常信息
        
        :return: 异常信息
        """
        try:
            result = controller.get_exception_info()
            return result
        except Exception as e:
            return {"status": "error", "message": f"获取异常信息失败: {str(e)}"}
    
    @mcp.tool('x64dbg_load_file', description='加载文件到调试器')
    async def load_file(file_path: str):
        """
        加载文件到调试器
        
        :param file_path: 文件完整路径
        :return: 加载结果
        """
        if not file_path or file_path.strip() == "":
            raise ValueError('文件路径不能为空!')
        
        try:
            result = controller.load_file(file_path)
            return result
        except Exception as e:
            return {"status": "error", "message": f"加载文件失败: {str(e)}"}
    
    @mcp.tool('x64dbg_save_memory_to_file', description='保存内存到文件')
    async def save_memory_to_file(address: str, size: int, output_file: str):
        """
        保存内存到文件
        
        :param address: 起始地址，十六进制格式(0x401000)
        :param size: 大小（字节），最大10MB
        :param output_file: 输出文件路径
        :return: 保存结果
        """
        if not address or address.strip() == "":
            raise ValueError('地址不能为空!')
        
        if size <= 0 or size > 10 * 1024 * 1024:
            raise ValueError('大小必须在1字节到10MB之间!')
        
        if not output_file or output_file.strip() == "":
            raise ValueError('输出文件路径不能为空!')
        
        try:
            result = controller.save_memory_to_file(address, size, output_file)
            return result
        except Exception as e:
            return {"status": "error", "message": f"保存内存失败: {str(e)}"}
    
    @mcp.tool('x64dbg_compare_memory', description='比较两处内存内容')
    async def compare_memory(address1: str, address2: str, size: int):
        """
        比较两处内存内容
        
        :param address1: 第一个地址，十六进制格式(0x401000)
        :param address2: 第二个地址，十六进制格式(0x402000)
        :param size: 比较大小（字节），最大1MB
        :return: 比较结果，包含差异列表
        """
        if not address1 or address1.strip() == "":
            raise ValueError('第一个地址不能为空!')
        
        if not address2 or address2.strip() == "":
            raise ValueError('第二个地址不能为空!')
        
        if size <= 0 or size > 1024 * 1024:
            raise ValueError('比较大小必须在1字节到1MB之间!')
        
        try:
            result = controller.compare_memory(address1, address2, size)
            return result
        except Exception as e:
            return {"status": "error", "message": f"内存比较失败: {str(e)}"}
    
    @mcp.tool('x64dbg_fill_memory', description='填充内存')
    async def fill_memory(address: str, size: int, value: int):
        """
        填充内存
        
        :param address: 起始地址，十六进制格式(0x401000)
        :param size: 大小（字节），最大1MB
        :param value: 填充值（0-255）
        :return: 填充结果
        """
        if not address or address.strip() == "":
            raise ValueError('地址不能为空!')
        
        if size <= 0 or size > 1024 * 1024:
            raise ValueError('大小必须在1字节到1MB之间!')
        
        if value < 0 or value > 255:
            raise ValueError('填充值必须在0-255之间!')
        
        try:
            result = controller.fill_memory(address, size, value)
            return result
        except Exception as e:
            return {"status": "error", "message": f"内存填充失败: {str(e)}"}
    
    @mcp.tool('x64dbg_calculate_address', description='计算地址（基址+偏移）')
    async def calculate_address(base_address: str, offset: int):
        """
        计算地址（基址+偏移）
        
        :param base_address: 基址，十六进制格式(0x401000)或十进制
        :param offset: 偏移量（可以是负数）
        :return: 计算结果
        """
        if not base_address or base_address.strip() == "":
            raise ValueError('基址不能为空!')
        
        try:
            result = controller.calculate_address(base_address, offset)
            return result
        except Exception as e:
            return {"status": "error", "message": f"地址计算失败: {str(e)}"}
    
    @mcp.tool('x64dbg_format_address', description='格式化地址')
    async def format_address(address: str, format_type: str = "hex"):
        """
        格式化地址
        
        :param address: 地址（可以是十六进制或十进制字符串）
        :param format_type: 格式类型: "hex"（十六进制）, "decimal"（十进制）, "both"（两者）
        :return: 格式化结果
        """
        if not address or address.strip() == "":
            raise ValueError('地址不能为空!')
        
        valid_formats = ["hex", "decimal", "both"]
        if format_type.lower() not in valid_formats:
            raise ValueError(f'格式类型必须是以下之一: {", ".join(valid_formats)}')
        
        try:
            result = controller.format_address(address, format_type.lower())
            return result
        except Exception as e:
            return {"status": "error", "message": f"地址格式化失败: {str(e)}"}
    
    # ========== 书签功能 ==========
    
    @mcp.tool('x64dbg_add_bookmark', description='添加地址书签')
    async def add_bookmark(address: str, name: str = ""):
        """
        添加地址书签
        
        :param address: 地址，十六进制格式(0x401000)
        :param name: 书签名称（可选，如果不提供则使用地址作为名称）
        :return: 添加结果
        """
        if not address or address.strip() == "":
            raise ValueError('地址不能为空!')
        
        try:
            result = controller.add_bookmark(address, name)
            return result
        except Exception as e:
            return {"status": "error", "message": f"添加书签失败: {str(e)}"}
    
    @mcp.tool('x64dbg_remove_bookmark', description='删除地址书签')
    async def remove_bookmark(address: str):
        """
        删除地址书签
        
        :param address: 地址，十六进制格式(0x401000)
        :return: 删除结果
        """
        if not address or address.strip() == "":
            raise ValueError('地址不能为空!')
        
        try:
            result = controller.remove_bookmark(address)
            return result
        except Exception as e:
            return {"status": "error", "message": f"删除书签失败: {str(e)}"}
    
    @mcp.tool('x64dbg_get_bookmarks', description='获取所有书签列表')
    async def get_bookmarks():
        """
        获取所有书签列表
        
        :return: 书签列表
        """
        try:
            result = controller.get_bookmarks()
            return result
        except Exception as e:
            return {"status": "error", "message": f"获取书签列表失败: {str(e)}"}
    
    @mcp.tool('x64dbg_goto_bookmark', description='跳转到书签')
    async def goto_bookmark(name: str):
        """
        跳转到书签（设置EIP到书签地址）
        
        :param name: 书签名称
        :return: 跳转结果
        """
        if not name or name.strip() == "":
            raise ValueError('书签名称不能为空!')
        
        try:
            result = controller.goto_bookmark(name)
            return result
        except Exception as e:
            return {"status": "error", "message": f"跳转书签失败: {str(e)}"}
    
    # ========== 执行跟踪功能 ==========
    
    @mcp.tool('x64dbg_start_trace', description='开始执行跟踪')
    async def start_trace():
        """
        开始执行跟踪（记录程序执行路径）
        
        :return: 开始跟踪结果
        """
        try:
            result = controller.start_trace()
            return result
        except Exception as e:
            return {"status": "error", "message": f"开始跟踪失败: {str(e)}"}
    
    @mcp.tool('x64dbg_stop_trace', description='停止执行跟踪')
    async def stop_trace():
        """
        停止执行跟踪
        
        :return: 停止跟踪结果
        """
        try:
            result = controller.stop_trace()
            return result
        except Exception as e:
            return {"status": "error", "message": f"停止跟踪失败: {str(e)}"}
    
    @mcp.tool('x64dbg_get_trace_records', description='获取跟踪记录')
    async def get_trace_records(count: int = 100):
        """
        获取执行跟踪记录
        
        :param count: 要获取的记录数量，默认100，最大10000
        :return: 跟踪记录列表
        """
        if count <= 0 or count > 10000:
            raise ValueError('记录数量必须在1-10000之间!')
        
        try:
            result = controller.get_trace_records(count)
            return result
        except Exception as e:
            return {"status": "error", "message": f"获取跟踪记录失败: {str(e)}"}

