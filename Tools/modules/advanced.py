"""
高级功能模块
提供高级功能相关的操作（反调试绕过、异常处理、日志等）
"""
from typing import Dict, Any
from ..core.base_controller import BaseController


class AdvancedModule:
    """高级功能模块"""
    
    def __init__(self, base_controller: BaseController):
        self.base = base_controller
    
    def bypass_antidebug(self, method: str = "all") -> Dict[str, Any]:
        """绕过反调试检测"""
        bypass_script = f"""# X64Dbg Anti-Debug Bypass Script
try:
    import dbg
    method = '{method}'
    
    results = {{}}
    
    if method in ['all', 'peb']:
        try:
            peb = dbg.getPEB()
            if peb:
                dbg.write(peb + 0x02, b'\\x00')
                results['peb'] = 'success'
        except:
            results['peb'] = 'failed'
    
    if method in ['all', 'ntquery']:
        try:
            ntdll = dbg.getModule('ntdll.dll')
            if ntdll:
                nt_query = dbg.getAddressFromSymbol('ntdll.NtQueryInformationProcess')
                results['ntquery'] = 'hook_required'
        except:
            results['ntquery'] = 'failed'
    
    if method in ['all', 'debugport']:
        try:
            peb = dbg.getPEB()
            if peb:
                debug_port_offset = 0x20
                dbg.write(peb + debug_port_offset, b'\\x00\\x00\\x00\\x00\\x00\\x00\\x00\\x00')
                results['debugport'] = 'success'
        except:
            results['debugport'] = 'failed'
    
    print(f"MCP_RESULT:{{'status':'success','method':'{method}','results':{{results}}}}")
except Exception as e:
    print(f"MCP_RESULT:{{'status':'error','error':str(e)}}")
"""
        return self.base.script_executor.execute_script_auto(bypass_script)
    
    def set_exception_handler(self, exception_code: int, action: str = "ignore") -> Dict[str, Any]:
        """设置异常处理"""
        handler_script = f"""# X64Dbg Exception Handler Script
try:
    import dbg
    exc_code = {exception_code}
    action = '{action}'
    
    if hasattr(dbg, 'setExceptionHandler'):
        result = dbg.setExceptionHandler(exc_code, action)
        print(f"MCP_RESULT:{{'status':'success','exception_code':{exception_code},'action':'{action}','result':result}}")
    else:
        result = dbgcmd(f'exception {{exc_code}}, {{action}}')
        print(f"MCP_RESULT:{{'status':'success','exception_code':{exception_code},'action':'{action}','result':result}}")
except Exception as e:
    print(f"MCP_RESULT:{{'status':'error','error':str(e)}}")
"""
        return self.base.script_executor.execute_script_auto(handler_script)
    
    def get_exception_info(self) -> Dict[str, Any]:
        """获取异常信息"""
        info_script = """# X64Dbg Get Exception Info Script
try:
    import dbg
    if hasattr(dbg, 'getExceptionInfo'):
        info = dbg.getExceptionInfo()
        print(f"MCP_RESULT:{'status':'success','info':info}")
    else:
        result = dbgcmd('exceptioninfo')
        print(f"MCP_RESULT:{'status':'success','result':result}")
except Exception as e:
    print(f"MCP_RESULT:{'status':'error','error':str(e)}")
"""
        return self.base.script_executor.execute_script_auto(info_script)
    
    def get_logs(self, count: int = 100) -> Dict[str, Any]:
        """获取x64dbg日志输出"""
        log_script = f"""# X64Dbg Get Logs Script
try:
    import dbg
    count = {count}
    
    if hasattr(dbg, 'getLogs'):
        logs = dbg.getLogs(count)
        print(f"MCP_RESULT:{{'status':'success','count':len(logs),'logs':logs}}")
    else:
        result = dbgcmd(f'log {{count}}')
        print(f"MCP_RESULT:{{'status':'success','count':{count},'result':result}}")
except Exception as e:
    print(f"MCP_RESULT:{{'status':'error','error':str(e)}}")
"""
        return self.base.script_executor.execute_script_auto(log_script)
    
    def capture_output(self, command: str) -> Dict[str, Any]:
        """捕获命令输出"""
        return self.base.execute_command(command, parse_result=True)

