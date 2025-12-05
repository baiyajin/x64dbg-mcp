"""
内存模块
提供内存相关的操作（读取、写入、搜索、转储、保护、分配、释放等）
"""
import os
from typing import Dict, Any, List, Optional
from ..core.base_controller import BaseController


class MemoryModule:
    """内存操作模块"""
    
    def __init__(self, base_controller: BaseController):
        """
        初始化内存模块
        
        :param base_controller: 基础控制器实例
        """
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
    
    def set_memory_protection(self, address: str, size: int, protection: str) -> Dict[str, Any]:
        """设置内存保护属性"""
        address = address.strip().replace(" ", "")
        protection_map = {
            "R": "PAGE_READONLY", "READ": "PAGE_READONLY",
            "W": "PAGE_READWRITE", "WRITE": "PAGE_READWRITE", "RW": "PAGE_READWRITE",
            "X": "PAGE_EXECUTE", "EXECUTE": "PAGE_EXECUTE",
            "RX": "PAGE_EXECUTE_READ",
            "RWX": "PAGE_EXECUTE_READWRITE",
            "NONE": "PAGE_NOACCESS"
        }
        prot_flag = protection_map.get(protection.upper(), protection)
        
        protect_script = f"""# X64Dbg Memory Protection Script
try:
    import dbg
    addr = int('{address}', 16) if '{address}'.startswith('0x') else int('{address}')
    size = {size}
    prot = '{prot_flag}'
    
    if hasattr(dbg, 'setMemoryProtection'):
        result = dbg.setMemoryProtection(addr, size, prot)
        print(f"MCP_RESULT:{{'status':'success','address':'{address}','size':{size},'protection':'{protection}','result':result}}")
    else:
        result = dbgcmd(f'VirtualProtect {{addr}}, {{size}}, {{prot}}')
        print(f"MCP_RESULT:{{'status':'success','address':'{address}','size':{size},'protection':'{protection}','result':result}}")
except Exception as e:
    print(f"MCP_RESULT:{{'status':'error','error':str(e)}}")
"""
        return self.base.script_executor.execute_script_auto(protect_script)
    
    def get_memory_protection(self, address: str) -> Dict[str, Any]:
        """获取内存保护属性"""
        address = address.strip().replace(" ", "")
        protect_script = f"""# X64Dbg Get Memory Protection Script
try:
    import dbg
    addr = int('{address}', 16) if '{address}'.startswith('0x') else int('{address}')
    
    if hasattr(dbg, 'getMemoryProtection'):
        prot = dbg.getMemoryProtection(addr)
        print(f"MCP_RESULT:{{'status':'success','address':'{address}','protection':prot}}")
    else:
        result = dbgcmd(f'VirtualQuery {{addr}}')
        print(f"MCP_RESULT:{{'status':'success','address':'{address}','result':result}}")
except Exception as e:
    print(f"MCP_RESULT:{{'status':'error','error':str(e)}}")
"""
        return self.base.script_executor.execute_script_auto(protect_script)
    
    def compare_memory(self, address1: str, address2: str, size: int) -> Dict[str, Any]:
        """比较两处内存内容"""
        address1 = address1.strip().replace(" ", "")
        address2 = address2.strip().replace(" ", "")
        
        compare_script = f"""# X64Dbg Memory Compare Script
try:
    import dbg
    addr1 = int('{address1}', 16) if '{address1}'.startswith('0x') else int('{address1}')
    addr2 = int('{address2}', 16) if '{address2}'.startswith('0x') else int('{address2}')
    size = {size}
    
    mem1 = dbg.read(addr1, size)
    mem2 = dbg.read(addr2, size)
    
    differences = []
    for i in range(size):
        if mem1[i] != mem2[i]:
            differences.append({{
                'offset': i,
                'address1': hex(addr1 + i),
                'address2': hex(addr2 + i),
                'value1': hex(mem1[i]),
                'value2': hex(mem2[i])
            }})
    
    result = {{
        'identical': len(differences) == 0,
        'total_bytes': size,
        'differences_count': len(differences),
        'differences': differences[:100]
    }}
    print(f"MCP_RESULT:{{'status':'success','result':{{result}}}}")
except Exception as e:
    print(f"MCP_RESULT:{{'status':'error','error':str(e)}}")
"""
        return self.base.script_executor.execute_script_auto(compare_script)
    
    def fill_memory(self, address: str, size: int, value: int) -> Dict[str, Any]:
        """填充内存"""
        address = address.strip().replace(" ", "")
        if value < 0 or value > 255:
            raise ValueError('填充值必须在0-255之间!')
        
        fill_script = f"""# X64Dbg Memory Fill Script
try:
    import dbg
    addr = int('{address}', 16) if '{address}'.startswith('0x') else int('{address}')
    size = {size}
    fill_value = {value}
    
    fill_data = bytes([fill_value] * size)
    dbg.write(addr, fill_data)
    
    print(f"MCP_RESULT:{{'status':'success','address':'{address}','size':{size},'value':{value}}")
except Exception as e:
    print(f"MCP_RESULT:{{'status':'error','error':str(e)}}")
"""
        return self.base.script_executor.execute_script_auto(fill_script)
    
    def allocate_memory(self, size: int, protection: str = "RWX") -> Dict[str, Any]:
        """分配内存"""
        if size <= 0 or size > 100 * 1024 * 1024:
            raise ValueError('内存大小必须在1字节到100MB之间!')
        
        alloc_script = f"""# X64Dbg Allocate Memory Script
try:
    import dbg
    size = {size}
    prot = '{protection}'
    
    if hasattr(dbg, 'malloc'):
        addr = dbg.malloc(size)
        if addr:
            if prot:
                dbg.setMemoryProtection(addr, size, prot)
            print(f"MCP_RESULT:{{'status':'success','address':hex(addr),'size':{size},'protection':'{protection}'}}")
        else:
            print(f"MCP_RESULT:{{'status':'error','error':'内存分配失败'}}")
    else:
        result = dbgcmd(f'alloc {{size}}, {{prot}}')
        print(f"MCP_RESULT:{{'status':'success','result':result}}")
except Exception as e:
    print(f"MCP_RESULT:{{'status':'error','error':str(e)}}")
"""
        return self.base.script_executor.execute_script_auto(alloc_script)
    
    def free_memory(self, address: str) -> Dict[str, Any]:
        """释放内存"""
        address = address.strip().replace(" ", "")
        free_script = f"""# X64Dbg Free Memory Script
try:
    import dbg
    addr = int('{address}', 16) if '{address}'.startswith('0x') else int('{address}')
    
    if hasattr(dbg, 'free'):
        result = dbg.free(addr)
        print(f"MCP_RESULT:{{'status':'success','address':'{address}','result':result}}")
    else:
        result = dbgcmd(f'free {{addr}}')
        print(f"MCP_RESULT:{{'status':'success','address':'{address}','result':result}}")
except Exception as e:
    print(f"MCP_RESULT:{{'status':'error','error':str(e)}}")
"""
        return self.base.script_executor.execute_script_auto(free_script)
    
    def get_memory_region_info(self, address: str) -> Dict[str, Any]:
        """获取内存区域信息"""
        address = address.strip().replace(" ", "")
        region_script = f"""# X64Dbg Get Memory Region Info Script
try:
    import dbg
    addr = int('{address}', 16) if '{address}'.startswith('0x') else int('{address}')
    
    if hasattr(dbg, 'getMemoryRegionInfo'):
        info = dbg.getMemoryRegionInfo(addr)
        print(f"MCP_RESULT:{{'status':'success','address':'{address}','info':{{info}}}}")
    else:
        result = dbgcmd(f'VirtualQuery {{addr}}')
        print(f"MCP_RESULT:{{'status':'success','address':'{address}','result':result}}")
except Exception as e:
    print(f"MCP_RESULT:{{'status':'error','error':str(e)}}")
"""
        return self.base.script_executor.execute_script_auto(region_script)
    
    def batch_read_memory(self, addresses: List[str], sizes: Optional[List[int]] = None) -> Dict[str, Any]:
        """批量读取内存"""
        if not addresses or len(addresses) == 0:
            raise ValueError('地址列表不能为空!')
        if len(addresses) > 100:
            raise ValueError('一次最多读取100个地址!')
        if sizes and len(sizes) != len(addresses):
            raise ValueError('大小列表长度必须与地址列表长度相同!')
        if not sizes:
            sizes = [64] * len(addresses)
        
        results = {}
        for i, addr in enumerate(addresses):
            size = sizes[i] if i < len(sizes) else 64
            result = self.read_memory(addr, size)
            results[addr] = result
        
        return {
            "status": "success",
            "total": len(addresses),
            "results": results
        }

