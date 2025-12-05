"""
内存基础操作模块
提供内存的基础操作（读取、写入、搜索、转储）
"""
import os
from typing import Dict, Any
from ..core.base_controller import BaseController


class MemoryBasicModule:
    """内存基础操作模块"""
    
    def __init__(self, base_controller: BaseController):
        self.base = base_controller
    
    def read_memory(self, address: str, size: int = 64) -> Dict[str, Any]:
        """读取内存"""
        address = address.strip().replace(" ", "")
        return self.base.execute_command(f"dump {address} {size}")
    
    def write_memory(self, address: str, data: str) -> Dict[str, Any]:
        """写入内存"""
        address = address.strip().replace(" ", "")
        return self.base.execute_command(f"write {address} {data}")
    
    def search_memory(self, pattern: str, start: str = "", end: str = "") -> Dict[str, Any]:
        """搜索内存"""
        if start and end:
            return self.base.execute_command(f"findmem {pattern} {start} {end}")
        else:
            return self.base.execute_command(f"findmem {pattern}")
    
    def dump_memory(self, address: str, size: int, output_file: str = "") -> Dict[str, Any]:
        """内存转储功能"""
        address = address.strip().replace(" ", "")
        if not output_file:
            output_file = os.path.join(
                self.base.script_executor.temp_script_dir,
                f"dump_{address.replace('0x', '').replace(' ', '')}_{size}.bin"
            )
        
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
        return self.base.script_executor.execute_script_auto(dump_script)

