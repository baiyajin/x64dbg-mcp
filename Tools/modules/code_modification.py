"""
代码修改模块
提供代码修改相关的操作（补丁、代码注入、DLL注入等）
"""
from typing import Dict, Any
from ..core.base_controller import BaseController


class CodeModificationModule:
    """代码修改模块"""
    
    def __init__(self, base_controller: BaseController):
        self.base = base_controller
    
    def apply_patch(self, address: str, data: str, description: str = "") -> Dict[str, Any]:
        """应用代码补丁"""
        address = address.strip().replace(" ", "")
        patch_script = f"""# X64Dbg Apply Patch Script
try:
    import dbg
    addr = int('{address}', 16) if '{address}'.startswith('0x') else int('{address}')
    patch_data = bytes.fromhex('{data.replace(' ', '')}')
    desc = '{description}'
    
    if hasattr(dbg, 'setPatch'):
        result = dbg.setPatch(addr, patch_data, desc)
        print(f"MCP_RESULT:{{'status':'success','address':'{address}','data':'{data}','description':'{description}','result':result}}")
    else:
        dbg.write(addr, patch_data)
        result = dbgcmd(f'patch {{addr}}, {{desc}}')
        print(f"MCP_RESULT:{{'status':'success','address':'{address}','data':'{data}','description':'{description}','result':result}}")
except Exception as e:
    print(f"MCP_RESULT:{{'status':'error','error':str(e)}}")
"""
        return self.base.script_executor.execute_script_auto(patch_script)
    
    def remove_patch(self, address: str) -> Dict[str, Any]:
        """移除代码补丁"""
        address = address.strip().replace(" ", "")
        remove_patch_script = f"""# X64Dbg Remove Patch Script
try:
    import dbg
    addr = int('{address}', 16) if '{address}'.startswith('0x') else int('{address}')
    
    if hasattr(dbg, 'removePatch'):
        result = dbg.removePatch(addr)
        print(f"MCP_RESULT:{{'status':'success','address':'{address}','result':result}}")
    else:
        result = dbgcmd(f'patchdel {{addr}}')
        print(f"MCP_RESULT:{{'status':'success','address':'{address}','result':result}}")
except Exception as e:
    print(f"MCP_RESULT:{{'status':'error','error':str(e)}}")
"""
        return self.base.script_executor.execute_script_auto(remove_patch_script)
    
    def get_patches(self) -> Dict[str, Any]:
        """获取所有补丁列表"""
        return self.base.execute_command("patchlist")
    
    def inject_code(self, address: str, shellcode: str, create_thread: bool = False) -> Dict[str, Any]:
        """注入代码（Shellcode）到目标进程"""
        address = address.strip().replace(" ", "") if address else ""
        inject_script = f"""# X64Dbg Code Injection Script
try:
    import dbg
    shellcode_hex = '{shellcode.replace(' ', '')}'
    shellcode_bytes = bytes.fromhex(shellcode_hex)
    
    if '{address}':
        addr = int('{address}', 16) if '{address}'.startswith('0x') else int('{address}')
    else:
        addr = dbg.malloc(len(shellcode_bytes))
    
    dbg.write(addr, shellcode_bytes)
    
    if {str(create_thread).lower()}:
        thread_id = dbg.createThread(addr)
        result = {{'address': hex(addr), 'thread_id': thread_id, 'executed': True}}
    else:
        old_eip = dbg.getRegister('EIP') if hasattr(dbg, 'getRegister') else None
        dbg.setRegister('EIP', addr)
        result = {{'address': hex(addr), 'executed': False, 'message': '代码已注入，需要手动执行'}}
        if old_eip:
            dbg.setRegister('EIP', old_eip)
    
    print(f"MCP_RESULT:{{'status':'success','result':{{result}}}}")
except Exception as e:
    import traceback
    error_msg = str(e) + "\\n" + traceback.format_exc()
    print(f"MCP_RESULT:{{'status':'error','error':'{{error_msg}}'}}")
"""
        return self.base.script_executor.execute_script_auto(inject_script)
    
    def inject_dll(self, dll_path: str, wait_for_load: bool = True) -> Dict[str, Any]:
        """注入DLL到目标进程"""
        inject_script = f"""# X64Dbg DLL Injection Script
try:
    import dbg
    import os
    dll_path = r"{dll_path}"
    
    if not os.path.exists(dll_path):
        raise FileNotFoundError(f"DLL文件不存在: {{dll_path}}")
    
    if hasattr(dbg, 'injectDLL'):
        result = dbg.injectDLL(dll_path, {str(wait_for_load).lower()})
        print(f"MCP_RESULT:{{'status':'success','dll_path':'{dll_path}','result':result}}")
    else:
        kernel32 = dbg.getModule('kernel32.dll')
        load_library = dbg.getAddressFromSymbol('kernel32.LoadLibraryA')
        path_bytes = dll_path.encode('utf-8') + b'\\x00'
        path_addr = dbg.malloc(len(path_bytes))
        dbg.write(path_addr, path_bytes)
        result = dbg.call(load_library, [path_addr])
        print(f"MCP_RESULT:{{'status':'success','dll_path':'{dll_path}','module_handle':hex(result) if result else None}}")
except Exception as e:
    import traceback
    error_msg = str(e) + "\\n" + traceback.format_exc()
    print(f"MCP_RESULT:{{'status':'error','error':'{{error_msg}}'}}")
"""
        return self.base.script_executor.execute_script_auto(inject_script)
    
    def eject_dll(self, dll_name: str) -> Dict[str, Any]:
        """卸载DLL"""
        eject_script = f"""# X64Dbg DLL Ejection Script
try:
    import dbg
    dll_name = '{dll_name}'
    
    module = dbg.getModule(dll_name)
    if not module:
        raise ValueError(f"模块未加载: {{dll_name}}")
    
    kernel32 = dbg.getModule('kernel32.dll')
    free_library = dbg.getAddressFromSymbol('kernel32.FreeLibrary')
    result = dbg.call(free_library, [module])
    print(f"MCP_RESULT:{{'status':'success','dll_name':'{dll_name}','result':result}}")
except Exception as e:
    import traceback
    error_msg = str(e) + "\\n" + traceback.format_exc()
    print(f"MCP_RESULT:{{'status':'error','error':'{{error_msg}}'}}")
"""
        return self.base.script_executor.execute_script_auto(eject_script)

