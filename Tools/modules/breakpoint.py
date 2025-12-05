"""
断点模块
提供断点相关的操作（软件断点、硬件断点、数据断点、条件断点等）
"""
from typing import Dict, Any, List
from ..core.base_controller import BaseController


class BreakpointModule:
    """断点操作模块"""
    
    def __init__(self, base_controller: BaseController):
        """
        初始化断点模块
        
        :param base_controller: 基础控制器实例
        """
        self.base = base_controller
    
    def set_breakpoint(self, address: str) -> Dict[str, Any]:
        """设置断点"""
        address = address.strip().replace(" ", "")
        return self.base.execute_command(f"bp {address}")
    
    def remove_breakpoint(self, address: str) -> Dict[str, Any]:
        """删除断点"""
        address = address.strip().replace(" ", "")
        return self.base.execute_command(f"bpc {address}")
    
    def enable_breakpoint(self, address: str) -> Dict[str, Any]:
        """启用断点"""
        address = address.strip().replace(" ", "")
        return self.base.execute_command(f"bpe {address}")
    
    def disable_breakpoint(self, address: str) -> Dict[str, Any]:
        """禁用断点"""
        address = address.strip().replace(" ", "")
        return self.base.execute_command(f"bpd {address}")
    
    def get_breakpoints(self) -> Dict[str, Any]:
        """获取所有断点列表"""
        return self.base.execute_command("bplist")
    
    def set_breakpoint_conditional(self, address: str, condition: str = "") -> Dict[str, Any]:
        """设置带条件的断点"""
        address = address.strip().replace(" ", "")
        if condition:
            # x64dbg支持条件断点，格式: bp address,condition
            return self.base.execute_command(f"bp {address},{condition}")
        else:
            return self.set_breakpoint(address)
    
    def get_breakpoint_hit_count(self, address: str) -> Dict[str, Any]:
        """获取断点命中计数"""
        address = address.strip().replace(" ", "")
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
        return self.base.script_executor.execute_script_auto(hit_count_script)
    
    def reset_breakpoint_hit_count(self, address: str) -> Dict[str, Any]:
        """重置断点命中计数"""
        address = address.strip().replace(" ", "")
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
        return self.base.script_executor.execute_script_auto(reset_script)
    
    def set_hardware_breakpoint(self, address: str, break_type: str = "execute", size: int = 1) -> Dict[str, Any]:
        """
        设置硬件断点
        
        :param address: 断点地址
        :param break_type: 断点类型，可选值: execute/e, write/w, read/r, readwrite/rw
        :param size: 断点大小（字节），可选值: 1, 2, 4, 8
        """
        address = address.strip().replace(" ", "")
        type_map = {
            "execute": "0", "e": "0",
            "write": "1", "w": "1",
            "read": "2", "r": "2",
            "readwrite": "3", "rw": "3"
        }
        bp_type = type_map.get(break_type.lower(), "0")
        if size not in [1, 2, 4, 8]:
            size = 1
        
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
        return self.base.script_executor.execute_script_auto(hwbp_script)
    
    def remove_hardware_breakpoint(self, address: str) -> Dict[str, Any]:
        """删除硬件断点"""
        address = address.strip().replace(" ", "")
        return self.base.execute_command(f"hwbpdel {address}")
    
    def set_watchpoint(self, address: str, watch_type: str = "write", size: int = 4) -> Dict[str, Any]:
        """
        设置数据断点（监视点）
        
        :param address: 监视地址
        :param watch_type: 监视类型，可选值: write/w, read/r, readwrite/rw
        :param size: 监视大小（字节），可选值: 1, 2, 4, 8
        """
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
    
    def batch_set_breakpoints(self, addresses: List[str]) -> Dict[str, Any]:
        """批量设置断点"""
        if not addresses or len(addresses) == 0:
            raise ValueError('地址列表不能为空!')
        if len(addresses) > 1000:
            raise ValueError('一次最多设置1000个断点!')
        
        results = {}
        for addr in addresses:
            result = self.set_breakpoint(addr)
            results[addr] = result
        
        success_count = sum(1 for r in results.values() if r.get("status") == "success")
        return {
            "status": "success",
            "total": len(addresses),
            "success": success_count,
            "failed": len(addresses) - success_count,
            "results": results
        }
    
    def batch_remove_breakpoints(self, addresses: List[str]) -> Dict[str, Any]:
        """批量删除断点"""
        if not addresses or len(addresses) == 0:
            raise ValueError('地址列表不能为空!')
        if len(addresses) > 1000:
            raise ValueError('一次最多删除1000个断点!')
        
        results = {}
        for addr in addresses:
            result = self.remove_breakpoint(addr)
            results[addr] = result
        
        success_count = sum(1 for r in results.values() if r.get("status") == "success")
        return {
            "status": "success",
            "total": len(addresses),
            "success": success_count,
            "failed": len(addresses) - success_count,
            "results": results
        }

