# gdbrpc

🌐 **Languages**: [English](README.md) | [中文](README.zh-CN.md)

一个基于 Python 的 RPC 框架，用于和 GDB 远程通信，远程调试 GDB 调试的目标

> [!NOTE]
> 虽然 gdbrpc 最先是为 NuttX RTOS 的调试工具开发，但实际上这是一个通用工具，可以被集成在任何使用了 GDB 的框架中作为新的 GDB 通信方式

**目录**

---

- [gdbrpc](#gdbrpc)
    - [Overview](#overview)
    - [Features](#features)
    - [Installation](#installation)
        - [From PyPI](#from-pypi)
        - [From Source](#from-source)
    - [Requirements](#requirements)
    - [Quick Start](#quick-start)
        - [Starting the GDB Server](#starting-the-gdb-server)
        - [Using the Python Client](#using-the-python-client)
        - [Using the Interactive CLI](#using-the-interactive-cli)
    - [TODO](#todo)
    - [Architecture](#architecture)
        - [Components](#components)
        - [Communication Flow](#communication-flow)
    - [API Reference](#api-reference)
        - [Client](#client)
        - [Request Classes](#request-classes)
    - [Configuration](#configuration)
        - [Server Configuration](#server-configuration)
        - [Client Configuration](#client-configuration)
    - [Troubleshooting](#troubleshooting)
    - [Contributing](#contributing)
    - [License](#license)
    - [Related Projects](#related-projects)
    - [Support](#support)

## Overview

gdbrpc 提供了一个 client-server 架构，允许开发者连接到一个已有的 GDB 调试会话中，同时 gdbrpc 提供了 Python API 用于让开发者在 GDB 上执行任意 Python 代码

## Features

- **远程控制 GDB**: 通过 socket 让 GDB 执行命令
- **GDB CLI**: 内置一个 GDB CLI 接口，用于提供和 GDB CLI 类似的体验
- **扩展性**: 提供了 Python API 用于执行命令，容易集成到 GDB 相关的其他框架中


## Installation

### From PyPI

```bash
pip install gdbrpc
```

### From Source

```bash
cd gdbrpc
pip install -e .
```

## Requirements

- Python >= 3.10
- GDB with Python support
- cloudpickle >= 0.0.0

## Quick Start

### Starting the GDB Server

在 GDB 会话中启动 gdbrpc

```gdb
(gdb) py import gdbrpc
(gdb) gdbrpc start
(gdb) gdbrpc start --port 20820 --host 0.0.0.0
(gdb) gdbrpc status
(gdb) gdbrpc stop
```

### Using the Python Client

```python
from gdbrpc import Client
from gdbrpc.utils import ShellExec

# Create and connect to the GDB server
client = Client(host="localhost", port=20819)
client.connect()

# Execute GDB commands
response = client.call(ShellExec("info threads"))
print(response)

# Get backtrace
bt = client.call(ShellExec("backtrace"))
print(bt)

# Evaluate expressions
result = client.call(ShellExec("print my_variable"))
print(result)

# Execute shell commands (prefix with !)
output = client.call(ShellExec("!ls -la"))
print(output)

# Close connection
client.disconnect()
```

### Using the Interactive CLI

gdbrpc 作为模块直接运行就是在启动 CLI 界面

```bash
# Connect to default server (localhost:20819)
python3 -m gdbrpc

# Connect to custom host and port
python3 -m gdbrpc --host 192.168.1.100 --port 20820

# Show help
python3 -m gdbrpc --help
```

连接后，你可以像操作 GDB CLI 一样操作它。当然这是 Python 简单模拟的 CLI 界面，所以不能和真正的 GDB CLI 相比

```
Welcome to the GDB Remote Protocol Client
Type `exit` or `quit` to disconnect.
Type `help` to show this help message.
If you need `interrupt` command to stop the target, use Ctrl+C.
gdb> info threads
  Id   Target Id                                Frame
* 1    process 1234 "myprogram"                 main () at main.c:42
gdb> backtrace
#0  main () at main.c:42
#1  0x00007ffff7a05b97 in __libc_start_main ()
gdb> print my_variable
$1 = 123
gdb> !ls
file1.txt  file2.txt  myprogram
gdb> exit
```

同样的，CLI 也提供了一些 API

```python
from gdbrpc import ClientCLI

cli = ClientCLI(host="localhost", port=20819)
cli.start()
```

**CLI Features:**
- 执行 GDB 命令
- 执行 shell，这里和 GDB 的还是一样的语法，即使用 `!` 或 `shell` 标明这个命令是一个 shell
- 使用 Ctrl+C 停止当前程序的运行

## TODO

- [ ] 让 CLI 有接近 GDB CLI 的体验
    - [ ] 自动补全
    - [ ] 命令历史记录
- [ ] 改进网络传输
    - [ ]  提升反序列化的安全性


> [!TODO]
> 架构、API 介绍等暂不翻译，为了防止后续 API 变化且 README 没有同步引发开发者的误解问题

## Troubleshooting

### 服务器无法启动

- 确认 GDB 已启用 Python 支持：`gdb --configuration | grep python`
- 检查端口是否已被占用：`netstat -an | grep 20819`
- 确认防火墙设置允许该连接

### 连接被拒绝

- 确认服务器正在运行：`(gdb) gdbrpc status`
- 检查客户端与服务器的主机/端口配置是否一致
- 确保客户端与服务器之间的网络连接正常

### 命令执行失败

- 确认 GDB 当前状态正确（例如程序已加载、正在运行）
- 检查命令语法是否符合当前 GDB 版本
- 查看服务器日志以获取详细错误信息
- 确保 GDB 使用的 Python 版本与客户端一致

## Contributing

欢迎任何贡献！错误报告、功能请求或者是代码提交等都可以提🤗

## License

Licensed under the Apache License, Version 2.0. See the LICENSE file for details.

## Related Projects

- [GDB Python API Documentation](https://sourceware.org/gdb/current/onlinedocs/gdb/Python-API.html)
- [pwndbg](https://github.com/pwndbg/pwndbg) - GDB plugin for exploit development
- [gdb-dashboard](https://github.com/cyrus-and/gdb-dashboard) - Modular GDB dashboard

## Support

For questions and support:
- Open an issue on the project repository
- Consult the GDB Python API documentation
- Review the examples in the `examples/` directory
