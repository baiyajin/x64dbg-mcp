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
    
    def execute_command(self, command: str, auto_execute: bool = True) -> Dict[str, Any]:
        """
        执行x64dbg命令
        通过创建Python脚本文件，x64dbg插件可以读取并执行
        如果auto_execute为True，尝试通过插件API自动执行
        
        :param command: 要执行的命令
        :param auto_execute: 是否尝试自动执行（默认True）
        """
        try:
            # 创建Python脚本内容
            # x64dbg的Python插件通常使用dbgcmd函数执行命令
            if auto_execute:
                # 尝试自动执行的脚本
                script_content = f"""# X64Dbg MCP Command Script (Auto Execute)
# Command: {command}
try:
    import dbg
    # 尝试通过API直接执行
    result = dbgcmd('{command}')
    print(f"MCP_RESULT:{{'status':'success','command':'{command}','result':result,'auto_executed':True}}")
except NameError:
    # 如果不在x64dbg环境中，保存脚本文件
    script_file = r"{self.temp_script_dir}\\mcp_cmd_{os.getpid()}.py"
    with open(script_file, 'w', encoding='utf-8') as f:
        f.write('''# X64Dbg MCP Command Script
try:
    result = dbgcmd('{command}')
    print(f"MCP_RESULT:{{'status':'success','command':'{command}','result':result}}")
except Exception as e:
    print(f"MCP_RESULT:{{'status':'error','command':'{command}','error':str(e)}}")
''')
    print(f"MCP_RESULT:{{'status':'pending','command':'{command}','script_file':'{{script_file}}','message':'脚本已保存，请在x64dbg中加载执行'}}")
except Exception as e:
    print(f"MCP_RESULT:{{'status':'error','command':'{command}','error':str(e)}}")
"""
                return self.execute_script_auto(script_content)
            else:
                # 传统方式：仅创建脚本文件
                script_content = f"""# X64Dbg MCP Command Script
# Command: {command}
try:
    result = dbgcmd('{command}')
    print(f"MCP_RESULT:{{'status':'success','command':'{command}','result':result}}")
except Exception as e:
    print(f"MCP_RESULT:{{'status':'error','command':'{command}','error':str(e)}}")
"""
                script_file = self._create_script_file(script_content)
                
                return {
                    "status": "success",
                    "command": command,
                    "script_file": script_file,
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
    
    def execute_script_auto(self, script_content: str) -> Dict[str, Any]:
        """
        自动执行脚本（通过插件API）
        尝试通过x64dbg的Python插件API自动执行脚本
        """
        try:
            # 转义脚本内容中的特殊字符
            escaped_content = script_content.replace('\\', '\\\\').replace("'", "\\'").replace('"', '\\"')
            script_file_path = os.path.join(self.temp_script_dir, f"mcp_auto_{os.getpid()}.py")
            
            # 创建增强的脚本，尝试自动执行
            auto_script = f"""# X64Dbg MCP Auto Execute Script
import os
import sys
try:
    # 尝试通过x64dbg Python API执行
    # 如果dbgcmd可用，说明在x64dbg环境中
    if 'dbgcmd' in globals() or 'dbg' in sys.modules:
        exec(compile('''{escaped_content}''', '<string>', 'exec'))
        print("MCP_RESULT:{{'status':'success','message':'脚本自动执行成功'}}")
    else:
        raise NameError("Not in x64dbg environment")
except NameError:
    # 如果不在x64dbg环境中，保存脚本文件
    script_file = r"{script_file_path}"
    with open(script_file, 'w', encoding='utf-8') as f:
        f.write('''{escaped_content}''')
    print(f"MCP_RESULT:{{'status':'pending','script_file':'{{script_file}}','message':'脚本已保存，请在x64dbg中加载执行'}}")
except Exception as e:
    print(f"MCP_RESULT:{{'status':'error','error':str(e)}}")
"""
            script_file = self._create_script_file(auto_script)
            return {
                "status": "success",
                "script_file": script_file,
                "message": "自动执行脚本已创建，如果x64dbg支持API调用将自动执行"
            }
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

