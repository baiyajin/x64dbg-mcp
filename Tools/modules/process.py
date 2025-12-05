"""
进程模块
提供进程相关的操作
"""
from typing import Dict, Any
from ..core.base_controller import BaseController


class ProcessModule:
    """进程操作模块"""
    
    def __init__(self, base_controller: BaseController):
        """
        初始化进程模块
        
        :param base_controller: 基础控制器实例
        """
        self.base = base_controller
    
    def get_debugger_status(self) -> Dict[str, Any]:
        """获取调试器实时状态"""
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
    print(f"MCP_RESULT:{'status':'success','data':{status}}")
except Exception as e:
    print(f"MCP_RESULT:{'status':'error','error':str(e)}")
"""
        return self.base.script_executor.execute_script_auto(status_script)
    
    def attach_process(self, process_id: int) -> Dict[str, Any]:
        """附加到进程"""
        attach_script = f"""# X64Dbg Attach Process Script
try:
    import dbg
    pid = {process_id}
    
    if hasattr(dbg, 'attachProcess'):
        result = dbg.attachProcess(pid)
        print(f"MCP_RESULT:{{'status':'success','pid':{process_id},'result':result}}")
    else:
        result = dbgcmd(f'attach {{pid}}')
        print(f"MCP_RESULT:{{'status':'success','pid':{process_id},'result':result}}")
except Exception as e:
    print(f"MCP_RESULT:{{'status':'error','error':str(e)}}")
"""
        return self.base.script_executor.execute_script_auto(attach_script)
    
    def detach_process(self) -> Dict[str, Any]:
        """分离当前调试的进程"""
        return self.base.execute_command("detach")

