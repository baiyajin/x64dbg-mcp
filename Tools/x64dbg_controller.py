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
from .modules.code_analysis import CodeAnalysisModule
from .modules.code_modification import CodeModificationModule
from .modules.debug_control import DebugControlModule
from .modules.information import InformationModule
from .modules.advanced import AdvancedModule
from .modules.utility import UtilityModule


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
        self.code_analysis = CodeAnalysisModule(self.base)
        self.code_modification = CodeModificationModule(self.base)
        self.debug_control = DebugControlModule(self.base)
        self.information = InformationModule(self.base)
        self.advanced = AdvancedModule(self.base)
        self.utility = UtilityModule(self.base)
        
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
        
        # 代码分析模块
        self.disassemble = self.code_analysis.disassemble
        self.resolve_symbol = self.code_analysis.resolve_symbol
        self.view_structure = self.code_analysis.view_structure
        self.evaluate_expression = self.code_analysis.evaluate_expression
        self.get_functions = self.code_analysis.get_functions
        self.get_labels = self.code_analysis.get_labels
        self.get_comments = self.code_analysis.get_comments
        
        # 代码修改模块
        self.apply_patch = self.code_modification.apply_patch
        self.remove_patch = self.code_modification.remove_patch
        self.get_patches = self.code_modification.get_patches
        self.inject_code = self.code_modification.inject_code
        self.inject_dll = self.code_modification.inject_dll
        self.eject_dll = self.code_modification.eject_dll
        
        # 调试控制模块
        self.step_over = self.debug_control.step_over
        self.step_into = self.debug_control.step_into
        self.continue_execution = self.debug_control.continue_execution
        self.pause_execution = self.debug_control.pause_execution
        self.start_trace = self.debug_control.start_trace
        self.stop_trace = self.debug_control.stop_trace
        self.get_trace_records = self.debug_control.get_trace_records
        self.start_profiling = self.debug_control.start_profiling
        self.stop_profiling = self.debug_control.stop_profiling
        self.get_profiling_results = self.debug_control.get_profiling_results
        
        # 信息获取模块
        self.get_modules = self.information.get_modules
        self.get_stack = self.information.get_stack
        self.get_call_stack = self.information.get_call_stack
        self.get_segments = self.information.get_segments
        self.get_strings = self.information.get_strings
        self.get_references = self.information.get_references
        self.get_imports = self.information.get_imports
        self.get_exports = self.information.get_exports
        
        # 高级功能模块
        self.bypass_antidebug = self.advanced.bypass_antidebug
        self.set_exception_handler = self.advanced.set_exception_handler
        self.get_exception_info = self.advanced.get_exception_info
        self.get_logs = self.advanced.get_logs
        self.capture_output = self.advanced.capture_output
        
        # 实用工具模块
        self.add_bookmark = self.utility.add_bookmark
        self.remove_bookmark = self.utility.remove_bookmark
        self.get_bookmarks = self.utility.get_bookmarks
        self.goto_bookmark = self.utility.goto_bookmark
        self.load_file = self.utility.load_file
        self.save_memory_to_file = self.utility.save_memory_to_file
        self.calculate_address = self.utility.calculate_address
        self.format_address = self.utility.format_address
        self.save_script = self.utility.save_script
        self.load_script = self.utility.load_script
        self.get_script_history = self.utility.get_script_history
        self.save_config = self.utility.save_config
        self.load_config = self.utility.load_config
        self.list_configs = self.utility.list_configs
        
        # 基础方法
        self.execute_command = self.base.execute_command
        self.execute_command_direct = self.base.execute_command_direct

