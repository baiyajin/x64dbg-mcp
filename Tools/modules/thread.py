"""
线程模块
提供线程相关的操作
"""
from typing import Dict, Any
from ..core.base_controller import BaseController


class ThreadModule:
    """线程操作模块"""
    
    def __init__(self, base_controller: BaseController):
        """
        初始化线程模块
        
        :param base_controller: 基础控制器实例
        """
        self.base = base_controller
    
    def get_threads(self) -> Dict[str, Any]:
        """获取线程列表"""
        return self.base.execute_command("thread")
    
    def switch_thread(self, thread_id: int) -> Dict[str, Any]:
        """切换当前线程"""
        switch_script = f"""# X64Dbg Switch Thread Script
try:
    import dbg
    tid = {thread_id}
    
    if hasattr(dbg, 'switchThread'):
        result = dbg.switchThread(tid)
        print(f"MCP_RESULT:{{'status':'success','thread_id':{thread_id},'result':result}}")
    else:
        result = dbgcmd(f'thread {{tid}}')
        print(f"MCP_RESULT:{{'status':'success','thread_id':{thread_id},'result':result}}")
except Exception as e:
    print(f"MCP_RESULT:{{'status':'error','error':str(e)}}")
"""
        return self.base.script_executor.execute_script_auto(switch_script)
    
    def suspend_thread(self, thread_id: int) -> Dict[str, Any]:
        """挂起线程"""
        suspend_script = f"""# X64Dbg Suspend Thread Script
try:
    import dbg
    tid = {thread_id}
    
    if hasattr(dbg, 'suspendThread'):
        result = dbg.suspendThread(tid)
        print(f"MCP_RESULT:{{'status':'success','thread_id':{thread_id},'result':result}}")
    else:
        result = dbgcmd(f'threadsuspend {{tid}}')
        print(f"MCP_RESULT:{{'status':'success','thread_id':{thread_id},'result':result}}")
except Exception as e:
    print(f"MCP_RESULT:{{'status':'error','error':str(e)}}")
"""
        return self.base.script_executor.execute_script_auto(suspend_script)
    
    def resume_thread(self, thread_id: int) -> Dict[str, Any]:
        """恢复线程"""
        resume_script = f"""# X64Dbg Resume Thread Script
try:
    import dbg
    tid = {thread_id}
    
    if hasattr(dbg, 'resumeThread'):
        result = dbg.resumeThread(tid)
        print(f"MCP_RESULT:{{'status':'success','thread_id':{thread_id},'result':result}}")
    else:
        result = dbgcmd(f'threadresume {{tid}}')
        print(f"MCP_RESULT:{{'status':'success','thread_id':{thread_id},'result':result}}")
except Exception as e:
    print(f"MCP_RESULT:{{'status':'error','error':str(e)}}")
"""
        return self.base.script_executor.execute_script_auto(resume_script)
    
    def get_thread_context(self, thread_id: int) -> Dict[str, Any]:
        """获取线程上下文"""
        context_script = f"""# X64Dbg Get Thread Context Script
try:
    import dbg
    tid = {thread_id}
    
    if hasattr(dbg, 'getThreadContext'):
        context = dbg.getThreadContext(tid)
        print(f"MCP_RESULT:{{'status':'success','thread_id':{thread_id},'context':{{context}}}}")
    else:
        result = dbgcmd(f'threadcontext {{tid}}')
        print(f"MCP_RESULT:{{'status':'success','thread_id':{thread_id},'result':result}}")
except Exception as e:
    print(f"MCP_RESULT:{{'status':'error','error':str(e)}}")
"""
        return self.base.script_executor.execute_script_auto(context_script)

