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
    
    def execute_command(self, command: str) -> Dict[str, Any]:
        """
        执行x64dbg命令
        通过创建Python脚本文件，x64dbg插件可以读取并执行
        """
        try:
            # 创建Python脚本内容
            # x64dbg的Python插件通常使用dbgcmd函数执行命令
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

