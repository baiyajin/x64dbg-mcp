"""
测试X64Dbg MCP服务
用于验证服务是否正常工作
"""
import sys
import os

# 添加项目路径
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

from Tools.x64dbg_tools import controller

def test_controller():
    """测试控制器基本功能"""
    print("=" * 50)
    print("X64Dbg MCP 服务测试")
    print("=" * 50)
    
    # 测试配置
    print(f"\n1. 检查配置:")
    print(f"   X64Dbg路径: {controller.x64dbg_path}")
    print(f"   插件目录: {controller.plugin_dir}")
    print(f"   临时脚本目录: {controller.temp_script_dir}")
    
    # 检查路径是否存在
    print(f"\n2. 检查路径:")
    if os.path.exists(controller.x64dbg_path):
        print(f"   ✓ X64Dbg可执行文件存在")
    else:
        print(f"   ✗ X64Dbg可执行文件不存在: {controller.x64dbg_path}")
        print(f"   请检查config.py中的X64DBG_PATH配置")
    
    if os.path.exists(controller.plugin_dir):
        print(f"   ✓ 插件目录存在")
    else:
        print(f"   ✗ 插件目录不存在: {controller.plugin_dir}")
        print(f"   请检查config.py中的X64DBG_PLUGIN_DIR配置")
    
    # 测试脚本创建
    print(f"\n3. 测试脚本创建:")
    try:
        test_script = controller._create_script_file("# 测试脚本\nprint('Hello from MCP')")
        if os.path.exists(test_script):
            print(f"   ✓ 脚本文件创建成功: {os.path.basename(test_script)}")
            # 清理测试文件
            try:
                os.remove(test_script)
                print(f"   ✓ 测试文件已清理")
            except:
                pass
        else:
            print(f"   ✗ 脚本文件创建失败")
    except Exception as e:
        print(f"   ✗ 脚本创建出错: {e}")
    
    # 测试命令执行
    print(f"\n4. 测试命令执行:")
    try:
        result = controller.execute_command("r")
        print(f"   ✓ 命令执行成功")
        print(f"   结果: {result.get('status', 'unknown')}")
        if 'script_file' in result:
            print(f"   脚本文件: {os.path.basename(result['script_file'])}")
    except Exception as e:
        print(f"   ✗ 命令执行出错: {e}")
    
    print(f"\n" + "=" * 50)
    print("测试完成！")
    print("=" * 50)
    print("\n提示:")
    print("1. 如果路径不存在，请修改config.py中的配置")
    print("2. 确保x64dbg已正确安装")
    print("3. 在x64dbg中加载生成的脚本文件来执行命令")

if __name__ == "__main__":
    test_controller()

