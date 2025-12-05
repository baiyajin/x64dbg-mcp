# X64Dbg MCP Server

X64Dbg的Model Context Protocol服务器，用于AI辅助逆向分析和调试。

## 功能特性

- ✅ 执行x64dbg调试命令
- ✅ 获取寄存器信息
- ✅ 获取模块列表
- ✅ 设置/删除断点
- ✅ 读取/写入内存
- ✅ 反汇编代码
- ✅ 单步调试（Step Over/Into）
- ✅ 继续/暂停执行
- ✅ 获取堆栈信息
- ✅ 搜索内存模式

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

编辑 `config.py`，设置正确的x64dbg安装路径：

```python
X64DBG_PATH = r"C:\Program Files\x64dbg\release\x64\x64dbg.exe"
X64DBG_PLUGIN_DIR = r"C:\Program Files\x64dbg\release\x64\plugins"
```

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

1. **脚本文件方式**：MCP服务创建Python脚本文件到x64dbg的plugins目录
2. **手动加载**：在x64dbg中通过 `File -> Script -> Load` 加载脚本执行命令
3. **自动执行**：如果x64dbg支持命令行参数或插件API，可以自动执行

### 脚本文件位置

脚本文件保存在：`[x64dbg安装目录]/release/x64/plugins/mcp_temp/`

## 可用工具

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

## 注意事项

1. **x64dbg必须已安装**：确保x64dbg已正确安装并配置路径
2. **Python插件**：x64dbg需要支持Python插件（通常自带）
3. **权限问题**：确保有权限在x64dbg插件目录创建文件
4. **手动操作**：某些操作可能需要手动在x64dbg中加载脚本文件
5. **调试模式**：建议在调试模式下使用，查看详细日志
6. **Cursor版本**：确保使用支持MCP的Cursor版本（通常需要较新版本）

## 故障排除

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

## 开发计划

- [ ] 支持自动执行脚本（通过插件API）
- [ ] 支持实时获取调试器状态
- [ ] 支持更多x64dbg命令
- [ ] 支持断点条件设置
- [ ] 支持内存转储功能
- [ ] 支持符号解析

## 许可证

本项目采用MIT许可证。

## 贡献

欢迎提交Issue和Pull Request！

## 相关链接

- [x64dbg官网](https://x64dbg.com/)
- [Model Context Protocol文档](https://modelcontextprotocol.io/)
- [FastMCP文档](https://github.com/jlowin/fastmcp)
- [Cursor MCP文档](https://docs.cursor.com/context/mcp)

