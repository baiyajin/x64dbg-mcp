"""
实用工具-管理模块
提供文件操作、地址工具、脚本管理、配置管理等功能
"""
import os
from typing import Dict, Any
from ..core.base_controller import BaseController


class UtilityManagementModule:
    """实用工具管理模块"""
    
    def __init__(self, base_controller: BaseController):
        self.base = base_controller
    
    def load_file(self, file_path: str) -> Dict[str, Any]:
        """加载文件到调试器"""
        load_script = f"""# X64Dbg Load File Script
try:
    import dbg
    import os
    file_path = r"{file_path}"
    
    if not os.path.exists(file_path):
        raise FileNotFoundError(f"文件不存在: {{file_path}}")
    
    if hasattr(dbg, 'loadFile'):
        result = dbg.loadFile(file_path)
        print(f"MCP_RESULT:{{'status':'success','file_path':'{file_path}','result':result}}")
    else:
        result = dbgcmd(f'open {{file_path}}')
        print(f"MCP_RESULT:{{'status':'success','file_path':'{file_path}','result':result}}")
except Exception as e:
    print(f"MCP_RESULT:{{'status':'error','error':str(e)}}")
"""
        return self.base.script_executor.execute_script_auto(load_script)
    
    def save_memory_to_file(self, address: str, size: int, output_file: str) -> Dict[str, Any]:
        """保存内存到文件"""
        from .memory_basic import MemoryBasicModule
        memory_module = MemoryBasicModule(self.base)
        return memory_module.dump_memory(address, size, output_file)
    
    def calculate_address(self, base_address: str, offset: int) -> Dict[str, Any]:
        """计算地址（基址+偏移）"""
        base_address = base_address.strip().replace(" ", "")
        try:
            base = int(base_address, 16) if base_address.startswith('0x') else int(base_address)
            result_addr = base + offset
            return {
                "status": "success",
                "base_address": base_address,
                "offset": offset,
                "result_address": hex(result_addr),
                "result_decimal": result_addr
            }
        except Exception as e:
            return {
                "status": "error",
                "message": f"地址计算失败: {str(e)}"
            }
    
    def format_address(self, address: str, format_type: str = "hex") -> Dict[str, Any]:
        """格式化地址"""
        address = address.strip().replace(" ", "")
        try:
            addr = int(address, 16) if address.startswith('0x') else int(address)
            
            formats = {
                "hex": hex(addr),
                "decimal": str(addr),
                "octal": oct(addr),
                "binary": bin(addr)
            }
            
            result = formats.get(format_type.lower(), hex(addr))
            return {
                "status": "success",
                "address": address,
                "format": format_type,
                "result": result
            }
        except Exception as e:
            return {
                "status": "error",
                "message": f"地址格式化失败: {str(e)}"
            }
    
    def save_script(self, script_content: str, file_path: str) -> Dict[str, Any]:
        """保存脚本到文件"""
        try:
            with open(file_path, 'w', encoding='utf-8') as f:
                f.write(script_content)
            return {
                "status": "success",
                "file_path": file_path,
                "message": f"脚本已保存到: {file_path}"
            }
        except Exception as e:
            return {
                "status": "error",
                "message": f"保存脚本失败: {str(e)}"
            }
    
    def load_script(self, file_path: str) -> Dict[str, Any]:
        """从文件加载脚本"""
        try:
            with open(file_path, 'r', encoding='utf-8') as f:
                content = f.read()
            return {
                "status": "success",
                "file_path": file_path,
                "content": content
            }
        except Exception as e:
            return {
                "status": "error",
                "message": f"加载脚本失败: {str(e)}"
            }
    
    def get_script_history(self, count: int = 20) -> Dict[str, Any]:
        """获取脚本执行历史"""
        if count <= 0 or count > 100:
            count = 20
        
        script_dir = self.base.script_executor.temp_script_dir
        try:
            files = sorted(
                [f for f in os.listdir(script_dir) if f.endswith('.py')],
                key=lambda x: os.path.getmtime(os.path.join(script_dir, x)),
                reverse=True
            )[:count]
            
            history = []
            for f in files:
                file_path = os.path.join(script_dir, f)
                history.append({
                    "file": f,
                    "path": file_path,
                    "modified": os.path.getmtime(file_path)
                })
            
            return {
                "status": "success",
                "count": len(history),
                "history": history
            }
        except Exception as e:
            return {
                "status": "error",
                "message": f"获取脚本历史失败: {str(e)}"
            }
    
    def save_config(self, config_name: str) -> Dict[str, Any]:
        """保存当前调试配置"""
        config_script = f"""# X64Dbg Save Config Script
try:
    import dbg
    config_name = '{config_name}'
    
    if hasattr(dbg, 'saveConfig'):
        result = dbg.saveConfig(config_name)
        print(f"MCP_RESULT:{{'status':'success','config_name':'{config_name}','result':result}}")
    else:
        result = dbgcmd(f'config save {{config_name}}')
        print(f"MCP_RESULT:{{'status':'success','config_name':'{config_name}','result':result}}")
except Exception as e:
    print(f"MCP_RESULT:{{'status':'error','error':str(e)}}")
"""
        return self.base.script_executor.execute_script_auto(config_script)
    
    def load_config(self, config_name: str) -> Dict[str, Any]:
        """加载调试配置"""
        config_script = f"""# X64Dbg Load Config Script
try:
    import dbg
    config_name = '{config_name}'
    
    if hasattr(dbg, 'loadConfig'):
        result = dbg.loadConfig(config_name)
        print(f"MCP_RESULT:{{'status':'success','config_name':'{config_name}','result':result}}")
    else:
        result = dbgcmd(f'config load {{config_name}}')
        print(f"MCP_RESULT:{{'status':'success','config_name':'{config_name}','result':result}}")
except Exception as e:
    print(f"MCP_RESULT:{{'status':'error','error':str(e)}}")
"""
        return self.base.script_executor.execute_script_auto(config_script)
    
    def list_configs(self) -> Dict[str, Any]:
        """获取所有配置列表"""
        config_script = """# X64Dbg List Configs Script
try:
    import dbg
    if hasattr(dbg, 'listConfigs'):
        configs = dbg.listConfigs()
        print(f"MCP_RESULT:{'status':'success','configs':configs}")
    else:
        result = dbgcmd('config list')
        print(f"MCP_RESULT:{'status':'success','result':result}")
except Exception as e:
    print(f"MCP_RESULT:{'status':'error','error':str(e)}")
"""
        return self.base.script_executor.execute_script_auto(config_script)

