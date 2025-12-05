"""
结果解析模块
负责解析x64dbg脚本执行结果
"""
import json
import re
from typing import Dict, Any


class ResultParser:
    """解析脚本执行结果"""
    
    @staticmethod
    def parse_script_result(output: str) -> Dict[str, Any]:
        """
        解析脚本执行结果
        从输出中提取MCP_RESULT JSON数据
        
        :param output: 脚本输出内容
        :return: 解析后的结果字典
        """
        try:
            # 查找MCP_RESULT标记
            pattern = r'MCP_RESULT:(\{.*?\})'
            matches = re.findall(pattern, output, re.DOTALL)
            if matches:
                # 尝试解析最后一个结果
                result_str = matches[-1]
                try:
                    result = json.loads(result_str)
                    return result
                except json.JSONDecodeError:
                    # 如果JSON解析失败，尝试修复常见的转义问题
                    result_str = result_str.replace("'", '"')
                    try:
                        result = json.loads(result_str)
                        return result
                    except:
                        pass
            
            # 如果没有找到MCP_RESULT，返回原始输出
            return {
                "status": "success",
                "raw_output": output,
                "message": "脚本执行完成，但未找到结构化结果"
            }
        except Exception as e:
            return {
                "status": "error",
                "message": f"解析脚本结果失败: {str(e)}",
                "raw_output": output
            }

