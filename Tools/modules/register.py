"""
寄存器模块
提供寄存器相关的操作
"""
from typing import Dict, Any
from ..core.base_controller import BaseController


class RegisterModule:
    """寄存器操作模块"""
    
    def __init__(self, base_controller: BaseController):
        """
        初始化寄存器模块
        
        :param base_controller: 基础控制器实例
        """
        self.base = base_controller
    
    def get_registers(self) -> Dict[str, Any]:
        """获取寄存器信息"""
        return self.base.execute_command("r")
    
    def set_register(self, register_name: str, value: str) -> Dict[str, Any]:
        """
        设置单个寄存器值
        
        :param register_name: 寄存器名称（如: eax, ebx, eip, rax等）
        :param value: 寄存器值（可以是十六进制0x401000或十进制）
        :return: 设置结果
        """
        register_name = register_name.strip().lower()
        value = value.strip()
        
        # 验证寄存器名称
        valid_registers = ['eax', 'ebx', 'ecx', 'edx', 'esi', 'edi', 'esp', 'ebp',
                          'eip', 'rax', 'rbx', 'rcx', 'rdx', 'rsi', 'rdi', 'rsp',
                          'rbp', 'rip', 'r8', 'r9', 'r10', 'r11', 'r12', 'r13',
                          'r14', 'r15', 'eflags', 'rflags']
        
        if register_name not in valid_registers:
            return {
                "status": "error",
                "message": f"无效的寄存器名称: {register_name}。支持的寄存器: {', '.join(valid_registers)}"
            }
        
        # 构建命令：set register value
        command = f"set {register_name}={value}"
        return self.base.execute_command(command)
    
    def set_registers(self, registers: Dict[str, str]) -> Dict[str, Any]:
        """
        批量设置多个寄存器值
        
        :param registers: 寄存器字典，格式: {"eax": "0x401000", "ebx": "0x402000"}
        :return: 批量设置结果
        """
        if not registers:
            return {
                "status": "error",
                "message": "寄存器字典不能为空"
            }
        
        results = {}
        success_count = 0
        error_count = 0
        
        for reg_name, reg_value in registers.items():
            result = self.set_register(reg_name, reg_value)
            results[reg_name] = result
            if result.get("status") == "success":
                success_count += 1
            else:
                error_count += 1
        
        return {
            "status": "success" if error_count == 0 else "partial",
            "total": len(registers),
            "success": success_count,
            "error": error_count,
            "results": results
        }

