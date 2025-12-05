"""
实用工具-书签模块
提供书签相关的操作
"""
from typing import Dict, Any
from ..core.base_controller import BaseController


class UtilityBookmarkModule:
    """书签操作模块"""
    
    def __init__(self, base_controller: BaseController):
        self.base = base_controller
    
    def add_bookmark(self, address: str, name: str = "") -> Dict[str, Any]:
        """添加地址书签"""
        address = address.strip().replace(" ", "")
        if not name:
            name = address
        
        bookmark_script = f"""# X64Dbg Bookmark Script
try:
    import dbg
    addr = int('{address}', 16) if '{address}'.startswith('0x') else int('{address}')
    bookmark_name = '{name}'
    
    if hasattr(dbg, 'setBookmark'):
        result = dbg.setBookmark(addr, bookmark_name)
        print(f"MCP_RESULT:{{'status':'success','address':'{address}','name':'{name}','result':result}}")
    else:
        result = dbgcmd(f'bookmark {{addr}}, {{bookmark_name}}')
        print(f"MCP_RESULT:{{'status':'success','address':'{address}','name':'{name}','result':result}}")
except Exception as e:
    print(f"MCP_RESULT:{{'status':'error','error':str(e)}}")
"""
        return self.base.script_executor.execute_script_auto(bookmark_script)
    
    def remove_bookmark(self, address: str) -> Dict[str, Any]:
        """删除地址书签"""
        address = address.strip().replace(" ", "")
        remove_script = f"""# X64Dbg Remove Bookmark Script
try:
    import dbg
    addr = int('{address}', 16) if '{address}'.startswith('0x') else int('{address}')
    
    if hasattr(dbg, 'removeBookmark'):
        result = dbg.removeBookmark(addr)
        print(f"MCP_RESULT:{{'status':'success','address':'{address}','result':result}}")
    else:
        result = dbgcmd(f'bookmarkdel {{addr}}')
        print(f"MCP_RESULT:{{'status':'success','address':'{address}','result':result}}")
except Exception as e:
    print(f"MCP_RESULT:{{'status':'error','error':str(e)}}")
"""
        return self.base.script_executor.execute_script_auto(remove_script)
    
    def get_bookmarks(self) -> Dict[str, Any]:
        """获取所有书签列表"""
        return self.base.execute_command("bookmarklist")
    
    def goto_bookmark(self, name: str) -> Dict[str, Any]:
        """跳转到书签"""
        goto_script = f"""# X64Dbg Goto Bookmark Script
try:
    import dbg
    bookmark_name = '{name}'
    
    if hasattr(dbg, 'getBookmarkAddress'):
        addr = dbg.getBookmarkAddress(bookmark_name)
        if addr:
            dbg.setRegister('EIP', addr)
            print(f"MCP_RESULT:{{'status':'success','name':'{name}','address':hex(addr)}}")
        else:
            print(f"MCP_RESULT:{{'status':'error','error':'书签不存在'}}")
    else:
        result = dbgcmd(f'bookmarkgoto {{bookmark_name}}')
        print(f"MCP_RESULT:{{'status':'success','name':'{name}','result':result}}")
except Exception as e:
    print(f"MCP_RESULT:{{'status':'error','error':str(e)}}")
"""
        return self.base.script_executor.execute_script_auto(goto_script)

