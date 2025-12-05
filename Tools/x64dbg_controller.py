"""
X64Dbg主控制器
整合所有功能模块，提供统一的接口
"""
from .core.base_controller import BaseController
from .modules.register import RegisterModule
from .modules.breakpoint import BreakpointModule
from .modules.memory import MemoryModule
from .modules.thread import ThreadModule
from .modules.process import ProcessModule


class X64DbgController:
    """X64Dbg主控制器，整合所有功能模块"""
    
    def __init__(self):
        """初始化主控制器"""
        self.base = BaseController()
        
        # 初始化所有功能模块
        self.register = RegisterModule(self.base)
        self.breakpoint = BreakpointModule(self.base)
        self.memory = MemoryModule(self.base)
        self.thread = ThreadModule(self.base)
        self.process = ProcessModule(self.base)
        
        # 为了向后兼容，将模块方法直接暴露在控制器上
        self._expose_module_methods()
    
    def _expose_module_methods(self):
        """将模块方法暴露到控制器上，保持向后兼容"""
        # 寄存器模块
        self.get_registers = self.register.get_registers
        self.set_register = self.register.set_register
        self.set_registers = self.register.set_registers
        
        # 断点模块
        self.set_breakpoint = self.breakpoint.set_breakpoint
        self.remove_breakpoint = self.breakpoint.remove_breakpoint
        self.enable_breakpoint = self.breakpoint.enable_breakpoint
        self.disable_breakpoint = self.breakpoint.disable_breakpoint
        self.get_breakpoints = self.breakpoint.get_breakpoints
        self.set_breakpoint_conditional = self.breakpoint.set_breakpoint_conditional
        self.get_breakpoint_hit_count = self.breakpoint.get_breakpoint_hit_count
        self.reset_breakpoint_hit_count = self.breakpoint.reset_breakpoint_hit_count
        self.set_hardware_breakpoint = self.breakpoint.set_hardware_breakpoint
        self.remove_hardware_breakpoint = self.breakpoint.remove_hardware_breakpoint
        self.set_watchpoint = self.breakpoint.set_watchpoint
        self.remove_watchpoint = self.breakpoint.remove_watchpoint
        self.batch_set_breakpoints = self.breakpoint.batch_set_breakpoints
        self.batch_remove_breakpoints = self.breakpoint.batch_remove_breakpoints
        
        # 内存模块
        self.read_memory = self.memory.read_memory
        self.write_memory = self.memory.write_memory
        self.search_memory = self.memory.search_memory
        self.dump_memory = self.memory.dump_memory
        self.set_memory_protection = self.memory.set_memory_protection
        self.get_memory_protection = self.memory.get_memory_protection
        self.compare_memory = self.memory.compare_memory
        self.fill_memory = self.memory.fill_memory
        self.allocate_memory = self.memory.allocate_memory
        self.free_memory = self.memory.free_memory
        self.get_memory_region_info = self.memory.get_memory_region_info
        self.batch_read_memory = self.memory.batch_read_memory
        
        # 线程模块
        self.get_threads = self.thread.get_threads
        self.switch_thread = self.thread.switch_thread
        self.suspend_thread = self.thread.suspend_thread
        self.resume_thread = self.thread.resume_thread
        self.get_thread_context = self.thread.get_thread_context
        
        # 进程模块
        self.get_debugger_status = self.process.get_debugger_status
        self.attach_process = self.process.attach_process
        self.detach_process = self.process.detach_process
        
        # 基础方法
        self.execute_command = self.base.execute_command
        self.execute_command_direct = self.base.execute_command_direct

