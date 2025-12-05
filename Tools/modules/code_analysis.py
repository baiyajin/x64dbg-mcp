"""
代码分析模块
提供代码分析相关的操作（反汇编、符号解析、结构体查看、表达式计算等）
"""
from typing import Dict, Any
from ..core.base_controller import BaseController


class CodeAnalysisModule:
    """代码分析模块"""
    
    def __init__(self, base_controller: BaseController):
        self.base = base_controller
    
    def disassemble(self, address: str, count: int = 10) -> Dict[str, Any]:
        """反汇编代码"""
        address = address.strip().replace(" ", "")
        return self.base.execute_command(f"disasm {address} {count}")
    
    def resolve_symbol(self, symbol: str) -> Dict[str, Any]:
        """解析符号地址"""
        resolve_script = f"""# X64Dbg Symbol Resolution Script
try:
    import dbg
    addr = dbg.getAddressFromSymbol('{symbol}')
    if addr:
        print(f"MCP_RESULT:{{'status':'success','symbol':'{symbol}','address':hex(addr)}}")
    else:
        result = dbgcmd('sym.fromname({symbol})')
        print(f"MCP_RESULT:{{'status':'success','symbol':'{symbol}','result':result}}")
except Exception as e:
    print(f"MCP_RESULT:{{'status':'error','error':str(e)}}")
"""
        return self.base.script_executor.execute_script_auto(resolve_script)
    
    def view_structure(self, address: str, structure_type: str = "auto") -> Dict[str, Any]:
        """查看结构体数据"""
        address = address.strip().replace(" ", "")
        struct_script = f"""# X64Dbg View Structure Script
try:
    import dbg
    addr = int('{address}', 16) if '{address}'.startswith('0x') else int('{address}')
    struct_type = '{structure_type}'
    
    structures = {{
        'PEB': {{'BeingDebugged': (0x02, 1), 'ProcessHeap': (0x30, 8), 'Ldr': (0x18, 8)}},
        'TEB': {{'ProcessEnvironmentBlock': (0x30, 8), 'ThreadLocalStorage': (0x58, 8), 'LastErrorValue': (0x68, 4)}}
    }}
    
    if struct_type.upper() in structures:
        struct_def = structures[struct_type.upper()]
        result = {{}}
        for field_name, (offset, size) in struct_def.items():
            field_addr = addr + offset
            if size == 1: value = dbg.readByte(field_addr)
            elif size == 2: value = dbg.readWord(field_addr)
            elif size == 4: value = dbg.readDword(field_addr)
            elif size == 8: value = dbg.readQword(field_addr)
            else: value = dbg.read(field_addr, size)
            result[field_name] = {{'offset': offset, 'address': hex(field_addr), 'value': hex(value) if isinstance(value, int) else value, 'size': size}}
        print(f"MCP_RESULT:{{'status':'success','address':'{address}','type':'{structure_type}','fields':{{result}}}}")
    else:
        result = dbgcmd(f'struct {{addr}}, {{struct_type}}')
        print(f"MCP_RESULT:{{'status':'success','address':'{address}','type':'{structure_type}','result':result}}")
except Exception as e:
    print(f"MCP_RESULT:{{'status':'error','error':str(e)}}")
"""
        return self.base.script_executor.execute_script_auto(struct_script)
    
    def evaluate_expression(self, expression: str) -> Dict[str, Any]:
        """计算表达式"""
        if not expression or expression.strip() == "":
            raise ValueError('表达式不能为空!')
        
        eval_script = f"""# X64Dbg Evaluate Expression Script
try:
    import dbg
    expr = '{expression}'
    
    if hasattr(dbg, 'evaluateExpression'):
        result = dbg.evaluateExpression(expr)
        print(f"MCP_RESULT:{{'status':'success','expression':'{expression}','result':hex(result) if isinstance(result, int) else result}}")
    else:
        result = dbgcmd(f'calc {{expr}}')
        print(f"MCP_RESULT:{{'status':'success','expression':'{expression}','result':result}}")
except Exception as e:
    print(f"MCP_RESULT:{{'status':'error','error':str(e)}}")
"""
        return self.base.script_executor.execute_script_auto(eval_script)
    
    def get_functions(self) -> Dict[str, Any]:
        """获取函数列表"""
        return self.base.execute_command("function")
    
    def get_labels(self) -> Dict[str, Any]:
        """获取标签列表"""
        return self.base.execute_command("label")
    
    def get_comments(self, address: str = "") -> Dict[str, Any]:
        """获取注释"""
        if address:
            return self.base.execute_command(f"comment {address}")
        else:
            return self.base.execute_command("comment")

