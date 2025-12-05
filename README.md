# X64Dbg MCP Server

<div align="center">
  <img src="logo.png" alt="X64Dbg MCP Logo" width="200">
</div>

X64Dbg的Model Context Protocol服务器，用于AI辅助逆向分析和调试。

## 功能特性

<details>
<summary>点击展开查看完整功能列表（共40+项）</summary>

- ✅ 执行x64dbg调试命令
- ✅ 获取寄存器信息
- ✅ 获取模块列表
- ✅ 设置/删除/启用/禁用断点
- ✅ 条件断点支持
- ✅ 读取/写入内存
- ✅ 内存保护属性管理
- ✅ 反汇编代码
- ✅ 单步调试（Step Over/Into）
- ✅ 继续/暂停执行
- ✅ 获取堆栈信息
- ✅ 搜索内存模式
- ✅ 脚本执行结果解析
- ✅ 日志输出捕获
- ✅ 内存转储功能
- ✅ 符号解析
- ✅ 硬件断点支持
- ✅ 数据断点（监视点）
- ✅ 进程附加/分离
- ✅ 代码补丁管理
- ✅ 代码注入（Shellcode注入）
- ✅ DLL注入/卸载
- ✅ 反调试绕过
- ✅ 异常处理设置
- ✅ 文件操作（加载/保存）
- ✅ 内存比较和填充
- ✅ 地址计算和格式化工具
- ✅ 寄存器值修改（单个/批量）
- ✅ 断点命中计数
- ✅ 书签管理
- ✅ 线程操作（切换/挂起/恢复/上下文）
- ✅ 执行跟踪
- ✅ 内存分配/释放
- ✅ 表达式计算
- ✅ 批量操作（断点/内存）
- ✅ 结构体查看
- ✅ 脚本管理
- ✅ 配置管理
- ✅ 性能分析

</details>

## 安装

### 1. 安装Python依赖

```bash
pip install -r requirements.txt
```

或使用uv（推荐）：

```bash
uv pip install -r requirements.txt
```

### 2. 配置x64dbg路径

#### 方法一：自动检测（推荐）

系统会自动检测以下常见路径：
- `D:\baiyajin-code\x64dbg\release\x64\x64dbg.exe` (开发环境)
- `C:\Program Files\x64dbg\release\x64\x64dbg.exe` (标准安装)
- `C:\Program Files (x86)\x64dbg\release\x64\x64dbg.exe` (32位系统)
- `%USERPROFILE%\x64dbg\release\x64\x64dbg.exe` (用户目录)
- `C:\x64dbg\release\x64\x64dbg.exe` (其他常见位置)
- `D:\x64dbg\release\x64\x64dbg.exe` (其他常见位置)
- 以及其他常见位置

如果x64dbg安装在上述位置之一，**无需额外配置**，系统会自动检测并使用。

#### 方法二：手动配置

如果x64dbg安装在其他位置，编辑 `config.py`，修改以下行：

```python
DEFAULT_X64DBG_PATH = r"你的x64dbg路径\x64dbg.exe"
DEFAULT_X64DBG_PLUGIN_DIR = r"你的x64dbg路径\plugins"
```

例如：
```python
DEFAULT_X64DBG_PATH = r"D:\MyTools\x64dbg\release\x64\x64dbg.exe"
DEFAULT_X64DBG_PLUGIN_DIR = r"D:\MyTools\x64dbg\release\x64\plugins"
```

#### 方法三：环境变量

设置环境变量 `X64DBG_PATH` 指向x64dbg.exe的完整路径：

**Windows PowerShell:**
```powershell
$env:X64DBG_PATH = "D:\baiyajin-code\x64dbg\release\x64\x64dbg.exe"
```

**Windows CMD:**
```cmd
set X64DBG_PATH=D:\baiyajin-code\x64dbg\release\x64\x64dbg.exe
```

**永久设置（系统环境变量）:**
1. 右键"此电脑" -> "属性" -> "高级系统设置" -> "环境变量"
2. 在"用户变量"或"系统变量"中添加：
   - 变量名：`X64DBG_PATH`
   - 变量值：`D:\baiyajin-code\x64dbg\release\x64\x64dbg.exe`

#### 验证配置

启动MCP服务器后，如果x64dbg未安装或路径错误，工具调用时会返回清晰的错误提示，指导用户如何配置。MCP服务器本身可以正常启动，只有在调用工具时才会提示需要配置x64dbg路径。

### 3. 安装x64dbg Python插件

确保x64dbg已安装Python插件（Python插件通常是x64dbg自带的）。

## 使用方法

### 在Cursor中配置（推荐）

Cursor支持通过项目配置文件或全局配置文件来设置MCP服务器。

#### 方法一：项目级配置（推荐）

1. **创建配置文件目录**

   在项目根目录下创建 `.cursor` 文件夹（如果不存在）：

   ```bash
   mkdir .cursor
   ```

2. **创建MCP配置文件**

   在 `.cursor` 文件夹中创建 `mcp.json` 文件，添加以下配置：

   ```json
   {
     "mcpServers": {
       "x64dbg-mcp": {
         "command": "python",
         "args": [
           "${workspaceFolder}/main.py"
         ],
         "env": {
           "PYTHONPATH": "${workspaceFolder}"
         }
       }
     }
   }
   ```

   **使用uv（推荐）**：

   ```json
   {
     "mcpServers": {
       "x64dbg-mcp": {
         "command": "uv",
         "args": [
           "run",
           "python",
           "${workspaceFolder}/main.py"
         ],
         "cwd": "${workspaceFolder}"
       }
     }
   }
   ```

3. **重启Cursor**

   保存配置文件后，重启Cursor IDE以使配置生效。

4. **验证配置**

   - 打开Cursor设置（`Ctrl+,` 或 `Cmd+,`）
   - 导航到 `Features` > `MCP` 或 `设置` > `功能` > `MCP`
   - 确认 `x64dbg-mcp` 服务器显示为已启用状态（绿色指示器）

#### 方法二：全局配置

1. **找到Cursor配置目录**

   - **Windows**: `%APPDATA%\Cursor\User\globalStorage\mcp.json` 或 `%USERPROFILE%\.cursor\mcp.json`
   - **macOS**: `~/Library/Application Support/Cursor/User/globalStorage/mcp.json` 或 `~/.cursor/mcp.json`
   - **Linux**: `~/.config/Cursor/User/globalStorage/mcp.json` 或 `~/.cursor/mcp.json`

2. **编辑全局配置文件**

   打开或创建 `mcp.json` 文件，添加以下配置（请将路径替换为你的实际项目路径）：

   ```json
   {
     "mcpServers": {
       "x64dbg-mcp": {
         "command": "python",
         "args": [
           "D:\\baiyajin-code\\x64dbg-mcp\\main.py"
         ],
         "env": {
           "PYTHONPATH": "D:\\baiyajin-code\\x64dbg-mcp"
         }
       }
     }
   }
   ```

   **使用uv（推荐）**：

   ```json
   {
     "mcpServers": {
       "x64dbg-mcp": {
         "command": "uv",
         "args": [
           "run",
           "python",
           "D:\\baiyajin-code\\x64dbg-mcp\\main.py"
         ],
         "cwd": "D:\\baiyajin-code\\x64dbg-mcp"
       }
     }
   }
   ```

3. **重启Cursor**

   保存配置文件后，重启Cursor IDE。

#### 配置说明

- **`command`**: 运行MCP服务器的命令（`python` 或 `uv`）
- **`args`**: 传递给命令的参数数组
  - `${workspaceFolder}`: Cursor会自动替换为当前工作区路径
  - 全局配置中需要使用绝对路径
- **`env`**: 环境变量（可选）
  - `PYTHONPATH`: 确保Python能找到项目模块
- **`cwd`**: 工作目录（使用uv时推荐设置）

#### 使用MCP工具

配置完成后，在Cursor的AI对话中可以直接使用x64dbg工具：

- "获取当前寄存器值"
- "在地址0x401000设置断点"
- "反汇编0x401000地址的代码"
- "读取0x401000地址的内存"

### 在Claude Desktop中配置

1. 打开Claude Desktop配置文件（Windows: `%APPDATA%\Claude\claude_desktop_config.json`）

2. 添加MCP服务器配置：

```json
{
  "mcpServers": {
    "x64dbg-mcp": {
      "command": "python",
      "args": [
        "D:\\baiyajin-code\\wx\\x64dbg-mcp\\main.py"
      ],
      "env": {
        "PYTHONPATH": "D:\\baiyajin-code\\wx\\x64dbg-mcp"
      }
    }
  }
}
```

或使用uv（推荐，会自动处理依赖）：

```json
{
  "mcpServers": {
    "x64dbg-mcp": {
      "command": "uv",
      "args": [
        "run",
        "python",
        "D:\\baiyajin-code\\wx\\x64dbg-mcp\\main.py"
      ],
      "cwd": "D:\\baiyajin-code\\wx\\x64dbg-mcp"
    }
  }
}
```

**注意**：请将路径 `D:\\baiyajin-code\\wx\\x64dbg-mcp` 替换为你的实际项目路径。

### 在Cherry Studio中配置

1. 打开Cherry Studio设置
2. 添加MCP服务器：
   - **名称**: X64Dbg-MCP-Server
   - **命令**: `python main.py` 或 `uv run python main.py`
   - **工作目录**: `D:\baiyajin-code\wx\x64dbg-mcp`
   - **环境变量**: 可选，设置PYTHONPATH

## 工作原理

### 命令执行方式

由于x64dbg主要通过GUI和插件系统工作，本MCP服务采用以下方式：

1. **自动执行（推荐）**：MCP服务尝试通过x64dbg的Python插件API自动执行脚本。如果x64dbg正在运行且支持API调用，命令将自动执行。
2. **脚本文件方式**：如果自动执行失败，MCP服务会创建Python脚本文件到x64dbg的plugins目录
3. **手动加载**：在x64dbg中通过 `File -> Script -> Load` 加载脚本执行命令（仅在自动执行不可用时需要）

### 脚本文件位置

脚本文件保存在：`[x64dbg安装目录]/release/x64/plugins/mcp_temp/`

### 自动执行机制

- 当x64dbg的Python插件环境可用时，脚本会自动执行
- 如果不在x64dbg环境中，脚本会保存到文件，等待手动加载
- 所有命令默认启用自动执行，可通过参数控制

## 项目结构

项目采用模块化设计，遵循单一职责原则，每个文件不超过200行。

```
Tools/
├── core/                      # 核心基础模块
│   ├── base_controller.py    # 基础控制器（命令执行）
│   ├── script_executor.py     # 脚本执行器
│   └── result_parser.py       # 结果解析器
├── modules/                   # 功能模块（按功能分类）
│   ├── register.py            # 寄存器操作
│   ├── breakpoint.py          # 断点管理
│   ├── memory.py              # 内存操作（组合模块）
│   ├── memory_basic.py        # 内存基础操作
│   ├── memory_advanced.py     # 内存高级操作
│   ├── thread.py              # 线程管理
│   ├── process.py             # 进程管理
│   ├── code_analysis.py       # 代码分析
│   ├── code_modification.py   # 代码修改
│   ├── debug_control.py       # 调试控制
│   ├── information.py         # 信息获取
│   ├── advanced.py            # 高级功能
│   ├── utility.py             # 实用工具（组合模块）
│   ├── utility_bookmark.py    # 书签操作
│   └── utility_management.py  # 管理功能（文件/脚本/配置）
├── registry/                  # 工具注册模块
│   └── tool_registry.py       # MCP工具注册
├── utils/                     # 共享工具模块
│   └── address_utils.py       # 地址工具函数
└── x64dbg_controller.py       # 主控制器（整合所有模块）
```

### 设计原则

1. **单一职责**：每个模块只负责一个功能领域
2. **文件大小限制**：每个文件不超过200行（部分组合模块除外）
3. **组合模式**：使用组合而非继承，便于扩展和维护
4. **向后兼容**：保持原有接口不变，确保现有代码正常工作

### 模块说明

- **core/**：提供基础功能，所有模块都依赖这些核心组件
- **modules/**：功能模块，每个模块封装一类相关功能
- **registry/**：负责将功能模块注册为MCP工具
- **utils/**：提供通用的工具函数，供各模块使用

## 可用工具

<details>
<summary>点击展开查看所有可用工具（共88个工具）</summary>

### x64dbg_execute_command
执行任意x64dbg调试命令

### x64dbg_get_registers
获取当前所有寄存器值

### x64dbg_get_modules
获取已加载的模块列表

### x64dbg_set_breakpoint
在指定地址设置断点

### x64dbg_remove_breakpoint
删除指定地址的断点

### x64dbg_read_memory
读取指定地址的内存内容

### x64dbg_write_memory
向指定地址写入内存数据

### x64dbg_disassemble
反汇编指定地址的代码

### x64dbg_step_over
单步执行（跳过函数调用）

### x64dbg_step_into
单步进入（进入函数调用）

### x64dbg_continue
继续执行程序

### x64dbg_pause
暂停程序执行

### x64dbg_get_stack
获取当前堆栈信息

### x64dbg_search_memory
在内存中搜索指定模式

### x64dbg_get_debugger_status
获取调试器实时状态（是否调试中、运行状态、当前PID/TID、地址等）

### x64dbg_set_breakpoint_conditional
设置带条件的断点（例如：当eax==0x100时触发）

### x64dbg_dump_memory
将内存转储到文件（支持最大10MB）

### x64dbg_resolve_symbol
解析符号名称到内存地址（例如：MessageBoxA, kernel32.CreateFile）

### x64dbg_get_threads
获取线程列表

### x64dbg_get_breakpoints
获取所有断点列表

### x64dbg_get_call_stack
获取调用栈信息

### x64dbg_get_segments
获取内存段信息

### x64dbg_get_strings
搜索字符串引用

### x64dbg_get_references
获取地址的交叉引用

### x64dbg_get_imports
获取导入函数列表

### x64dbg_get_exports
获取导出函数列表

### x64dbg_get_comments
获取注释信息

### x64dbg_get_labels
获取标签列表

### x64dbg_get_functions
获取函数列表

### x64dbg_enable_breakpoint
启用断点（如果断点被禁用）

### x64dbg_disable_breakpoint
禁用断点（不断点删除，只是临时禁用）

### x64dbg_capture_output
捕获命令执行的实际输出（增强版命令执行，包含输出解析）

### x64dbg_get_logs
获取x64dbg日志输出

### x64dbg_set_memory_protection
设置内存保护属性（可读、可写、可执行等）

### x64dbg_get_memory_protection
获取内存保护属性

### x64dbg_set_hardware_breakpoint
设置硬件断点（支持执行、写入、读取、读写断点）

### x64dbg_remove_hardware_breakpoint
删除硬件断点

### x64dbg_set_watchpoint
设置数据断点（监视点），用于监控内存访问

### x64dbg_remove_watchpoint
删除数据断点（监视点）

### x64dbg_attach_process
附加到正在运行的进程进行调试

### x64dbg_detach_process
分离当前调试的进程（不断点终止进程）

### x64dbg_apply_patch
应用代码补丁（修改代码）

### x64dbg_remove_patch
移除代码补丁（恢复原始代码）

### x64dbg_get_patches
获取所有补丁列表

### x64dbg_inject_code
注入代码（Shellcode）到目标进程

### x64dbg_inject_dll
注入DLL到目标进程

### x64dbg_eject_dll
卸载DLL（从目标进程中移除）

### x64dbg_bypass_antidebug
绕过反调试检测（修改PEB标志、绕过NtQuery等）

### x64dbg_set_exception_handler
设置异常处理（忽略/中断/记录特定异常）

### x64dbg_get_exception_info
获取当前异常信息

### x64dbg_load_file
加载文件到调试器

### x64dbg_save_memory_to_file
保存内存到文件

### x64dbg_compare_memory
比较两处内存内容（查找差异）

### x64dbg_fill_memory
填充内存（用指定值填充内存区域）

### x64dbg_calculate_address
计算地址（基址+偏移）

### x64dbg_format_address
格式化地址（十六进制/十进制转换）

### x64dbg_set_register
设置单个寄存器值

### x64dbg_set_registers
批量设置寄存器值

### x64dbg_get_breakpoint_hit_count
获取断点命中计数（断点被触发的次数）

### x64dbg_reset_breakpoint_hit_count
重置断点命中计数

### x64dbg_add_bookmark
添加地址书签

### x64dbg_remove_bookmark
删除地址书签

### x64dbg_get_bookmarks
获取所有书签列表

### x64dbg_goto_bookmark
跳转到书签地址

### x64dbg_switch_thread
切换当前线程

### x64dbg_suspend_thread
挂起线程

### x64dbg_resume_thread
恢复线程

### x64dbg_get_thread_context
获取线程上下文

### x64dbg_start_trace
开始执行跟踪

### x64dbg_stop_trace
停止执行跟踪

### x64dbg_get_trace_records
获取跟踪记录

### x64dbg_allocate_memory
在目标进程中分配内存

### x64dbg_free_memory
释放分配的内存

### x64dbg_get_memory_region_info
获取内存区域信息

### x64dbg_evaluate_expression
计算表达式（支持寄存器、内存地址、常量等）

### x64dbg_batch_set_breakpoints
批量设置断点

### x64dbg_batch_remove_breakpoints
批量删除断点

### x64dbg_batch_read_memory
批量读取内存

### x64dbg_view_structure
查看结构体数据（PEB、TEB等）

### x64dbg_save_script
保存脚本到文件

### x64dbg_load_script
从文件加载脚本

### x64dbg_get_script_history
获取脚本执行历史

### x64dbg_save_config
保存当前调试配置

### x64dbg_load_config
加载调试配置

### x64dbg_list_configs
获取所有配置列表

### x64dbg_start_profiling
开始性能分析

### x64dbg_stop_profiling
停止性能分析

### x64dbg_get_profiling_results
获取性能分析结果

</details>

## 注意事项

1. **x64dbg必须已安装**：确保x64dbg已正确安装并配置路径
2. **Python插件**：x64dbg需要支持Python插件（通常自带）
3. **权限问题**：确保有权限在x64dbg插件目录创建文件
4. **自动执行**：新版本支持自动执行脚本，如果x64dbg正在运行且支持API，命令会自动执行
5. **手动操作**：如果自动执行失败，某些操作可能需要手动在x64dbg中加载脚本文件
6. **调试模式**：建议在调试模式下使用，查看详细日志
7. **Cursor版本**：确保使用支持MCP的Cursor版本（通常需要较新版本）
8. **结果解析**：新版本支持自动解析脚本执行结果，获取实际输出内容

## 故障排除

<details>
<summary>点击展开查看故障排除指南</summary>

### 问题：找不到x64dbg路径

**解决方案**：
1. 检查 `config.py` 中的路径配置
2. 确保x64dbg已正确安装
3. 手动设置正确的路径

### 问题：无法创建脚本文件

**解决方案**：
1. 检查x64dbg插件目录的写入权限
2. 确保目录存在
3. 检查磁盘空间

### 问题：命令执行失败

**解决方案**：
1. 确保x64dbg已启动并加载了目标程序
2. 检查命令语法是否正确
3. 查看x64dbg的日志输出

### 问题：Cursor中MCP服务器未显示

**解决方案**：
1. 检查 `mcp.json` 文件格式是否正确（JSON格式）
2. 确认文件路径正确（项目级：`.cursor/mcp.json`，全局级：用户配置目录）
3. 重启Cursor IDE
4. 检查Cursor设置中的MCP功能是否已启用
5. 查看Cursor的输出面板（`View` > `Output`）查看MCP相关错误信息

### 问题：Python路径错误

**解决方案**：
1. 确保Python已正确安装并在PATH中
2. 使用完整路径指定Python解释器：
   ```json
   {
     "mcpServers": {
       "x64dbg-mcp": {
         "command": "C:\\Python\\python.exe",
         "args": ["${workspaceFolder}/main.py"]
       }
     }
   }
   ```
3. 如果使用虚拟环境，确保激活虚拟环境或使用虚拟环境的Python路径

</details>

## 更新日志

查看完整的提交历史：[Git提交记录](https://github.com/baiyajin/x64dbg-mcp/commits/main)

<details>
<summary>点击展开查看最近更新</summary>

- ✅ **docs: 移除已完成的开发计划部分** - 清理README，移除已完成的功能列表
- ✅ **chore: 优化FastMCP日志输出配置** - 减少日志输出，优化启动体验
- ✅ **feat: 添加智能x64dbg路径检测** - 支持自动检测x64dbg安装路径，未安装时提供友好提示
- ✅ **docs: 在README中添加项目logo** - 添加项目logo展示
- ✅ **修复: 解决异常消息中的中文乱码问题** - 修复编码问题，确保中文正确显示
- ✅ **修复: 解决日志乱码问题** - 配置UTF-8编码，解决日志输出乱码
- ✅ **修复: 解决MCP协议JSON解析错误问题** - 修复f-string语法错误
- ✅ **重构: 拆分大文件使其符合200行限制** - 模块化重构，遵循单一职责原则
- ✅ **配置: 添加Cursor MCP服务器配置文件** - 添加MCP服务器配置示例

</details>

## 许可证

本项目采用MIT许可证。

## 贡献

欢迎提交Issue和Pull Request！

## 支持项目

如果这个项目对你有帮助，欢迎通过微信赞赏支持开发者继续改进项目！

<div align="center">
  <img src="wechat_reward.jpg" alt="微信赞赏码" width="300">
  <p><em>你的鼓励是我改BUG的动力 💪</em></p>
</div>

## 技术支持

遇到问题需要帮助？欢迎加入付费技术支持咨询交流微信群，与开发者和其他用户交流！

<div align="center">
  <img src="wechat_group.jpg" alt="付费技术支持咨询交流微信群" width="300">
  <p><em>扫码加入微信群，获取技术支持 💬</em></p>
</div>

## 相关链接

- [x64dbg官网](https://x64dbg.com/)
- [Model Context Protocol文档](https://modelcontextprotocol.io/)
- [FastMCP文档](https://github.com/jlowin/fastmcp)
- [Cursor MCP文档](https://docs.cursor.com/context/mcp)
- [Git提交历史](https://github.com/baiyajin/x64dbg-mcp/commits/main)
- [GitHub仓库](https://github.com/baiyajin/x64dbg-mcp)

