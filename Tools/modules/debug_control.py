"""
调试控制模块
提供调试控制相关的操作（单步、继续、暂停、跟踪、性能分析等）
"""
from typing import Dict, Any
from ..core.base_controller import BaseController


class DebugControlModule:
    """调试控制模块"""
    
    def __init__(self, base_controller: BaseController):
        self.base = base_controller
    
    def step_over(self) -> Dict[str, Any]:
        """单步执行（Step Over）"""
        return self.base.execute_command("stepover")
    
    def step_into(self) -> Dict[str, Any]:
        """单步进入（Step Into）"""
        return self.base.execute_command("stepinto")
    
    def continue_execution(self) -> Dict[str, Any]:
        """继续执行"""
        return self.base.execute_command("run")
    
    def pause_execution(self) -> Dict[str, Any]:
        """暂停执行"""
        return self.base.execute_command("pause")
    
    def start_trace(self) -> Dict[str, Any]:
        """开始执行跟踪"""
        trace_script = """# X64Dbg Start Trace Script
try:
    import dbg
    if hasattr(dbg, 'startTrace'):
        result = dbg.startTrace()
        print(f"MCP_RESULT:{'status':'success','message':'跟踪已开始','result':result}")
    else:
        result = dbgcmd('trace')
        print(f"MCP_RESULT:{'status':'success','message':'跟踪已开始','result':result}")
except Exception as e:
    print(f"MCP_RESULT:{'status':'error','error':str(e)}")
"""
        return self.base.script_executor.execute_script_auto(trace_script)
    
    def stop_trace(self) -> Dict[str, Any]:
        """停止执行跟踪"""
        stop_script = """# X64Dbg Stop Trace Script
try:
    import dbg
    if hasattr(dbg, 'stopTrace'):
        result = dbg.stopTrace()
        print(f"MCP_RESULT:{'status':'success','message':'跟踪已停止','result':result}")
    else:
        result = dbgcmd('tracestop')
        print(f"MCP_RESULT:{'status':'success','message':'跟踪已停止','result':result}")
except Exception as e:
    print(f"MCP_RESULT:{'status':'error','error':str(e)}")
"""
        return self.base.script_executor.execute_script_auto(stop_script)
    
    def get_trace_records(self, count: int = 100) -> Dict[str, Any]:
        """获取跟踪记录"""
        if count <= 0 or count > 10000:
            count = 100
        
        records_script = f"""# X64Dbg Get Trace Records Script
try:
    import dbg
    count = {count}
    
    if hasattr(dbg, 'getTraceRecords'):
        records = dbg.getTraceRecords(count)
        print(f"MCP_RESULT:{{'status':'success','count':len(records),'records':records}}")
    else:
        result = dbgcmd(f'tracelist {{count}}')
        print(f"MCP_RESULT:{{'status':'success','count':{count},'result':result}}")
except Exception as e:
    print(f"MCP_RESULT:{{'status':'error','error':str(e)}}")
"""
        return self.base.script_executor.execute_script_auto(records_script)
    
    def start_profiling(self) -> Dict[str, Any]:
        """开始性能分析"""
        profiling_script = """# X64Dbg Start Profiling Script
try:
    import dbg
    if hasattr(dbg, 'startProfiling'):
        result = dbg.startProfiling()
        print(f"MCP_RESULT:{'status':'success','message':'性能分析已开始','result':result}")
    else:
        result = dbgcmd('profile start')
        print(f"MCP_RESULT:{'status':'success','message':'性能分析已开始','result':result}")
except Exception as e:
    print(f"MCP_RESULT:{'status':'error','error':str(e)}")
"""
        return self.base.script_executor.execute_script_auto(profiling_script)
    
    def stop_profiling(self) -> Dict[str, Any]:
        """停止性能分析"""
        stop_script = """# X64Dbg Stop Profiling Script
try:
    import dbg
    if hasattr(dbg, 'stopProfiling'):
        result = dbg.stopProfiling()
        print(f"MCP_RESULT:{'status':'success','message':'性能分析已停止','result':result}")
    else:
        result = dbgcmd('profile stop')
        print(f"MCP_RESULT:{'status':'success','message':'性能分析已停止','result':result}")
except Exception as e:
    print(f"MCP_RESULT:{'status':'error','error':str(e)}")
"""
        return self.base.script_executor.execute_script_auto(stop_script)
    
    def get_profiling_results(self) -> Dict[str, Any]:
        """获取性能分析结果"""
        results_script = """# X64Dbg Get Profiling Results Script
try:
    import dbg
    if hasattr(dbg, 'getProfilingResults'):
        results = dbg.getProfilingResults()
        print(f"MCP_RESULT:{'status':'success','results':results}")
    else:
        result = dbgcmd('profile results')
        print(f"MCP_RESULT:{'status':'success','result':result}")
except Exception as e:
    print(f"MCP_RESULT:{'status':'error','error':str(e)}")
"""
        return self.base.script_executor.execute_script_auto(results_script)

