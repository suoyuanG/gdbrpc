# gdbrpc

A Python-based RPC (Remote Procedure Call) framework for GDB (GNU Debugger) that enables programmatic control and automation of debugging sessions.

## Overview

`gdbrpc` provides a client-server architecture that allows you to control GDB instances remotely through a simple Python API. It's designed to be framework-agnostic and can be used with any GDB-compatible debugger, not limited to any specific operating system or embedded platform.

## Features

- **Remote GDB Control**: Execute GDB commands remotely via socket communication
- **Bidirectional Communication**: Client-server architecture with full duplex support
- **Command Serialization**: Uses cloudpickle for robust serialization of Python objects
- **Interactive CLI**: Built-in command-line interface for quick debugging sessions
- **Extensible**: Easy to integrate into custom debugging workflows and automation scripts

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

Within a GDB session, use the GDB commands (after importing gdbrpc):

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

The easiest way to interact with a GDB server is using the built-in CLI:

```bash
# Connect to default server (localhost:20819)
python3 -m gdbrpc

# Connect to custom host and port
python3 -m gdbrpc --host 192.168.1.100 --port 20820

# Show help
python3 -m gdbrpc --help
```

Once connected, you can type GDB commands directly:

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

Or use the CLI programmatically from Python:

```python
from gdbrpc import ClientCLI

cli = ClientCLI(host="localhost", port=20819)
cli.start()
```

**CLI Features:**
- Execute any GDB command interactively
- Run shell commands with `!` prefix (e.g., `!ls`, `!pwd`)
- Use Ctrl+C to send interrupt signal to target
- Tab completion and command history (if readline is available)
- Automatic reconnection handling

## Architecture

### Components

- **Server**: Runs inside GDB process, listens for incoming connections
- **Client**: Python client that connects to the server and sends commands
- **CLI**: Interactive command-line interface built on top of the client
- **Protocol**: Custom protocol for request/response communication using cloudpickle

### Communication Flow

```
┌─────────────┐         Socket         ┌─────────────┐
│   Client    │◄──────────────────────►│   Server    │
│  (Python)   │    (Port 20819)        │  (In GDB)   │
└─────────────┘                        └─────────────┘
      │                                       │
      │ Send Request                          │
      │──────────────────────────────────────►│
      │                                       │ Execute Command
      │                                       │ in GDB Context
      │                            Response   │
      │◄──────────────────────────────────────│
      │                                       │
```

## API Reference

### Client

#### `Client(host="localhost", port=20819, logLevel=logging.INFO)`

Create a new client instance.

**Parameters:**
- `host` (str): Server hostname or IP address (default: "localhost")
- `port` (int): Server port number (default: 20819)
- `logLevel` (int): Logging level (default: logging.INFO)

#### `connect() -> bool`

Establish connection to the GDB server.

**Returns:** `True` if connection successful, `False` otherwise

#### `call(request: Request, post_request: Optional[PostRequest] = None, timeout: float = 300) -> Any`

Send a request to the GDB server and receive response.

**Parameters:**
- `request` (Request): Request object to send (typically `ShellExec` for executing commands)
- `post_request` (Optional[PostRequest]): Optional callback request for async handling
- `timeout` (float): Request timeout in seconds (default: 300)

**Returns:** Response payload from the server

**Example:**
```python
from gdbrpc import Client
from gdbrpc.utils import ShellExec

client = Client("localhost", 20819)
client.connect()

# Execute GDB command
result = client.call(ShellExec("info threads"))
print(result)

# Execute shell command (prefix with !)
result = client.call(ShellExec("!ls -la"))
print(result)
```

#### `disconnect()`

Close the connection to the server and cleanup resources.

### Request Classes

#### `ShellExec(command: str)`

Request to execute a GDB command or shell command on the server.

**Parameters:**
- `command` (str): Command to execute
  - GDB commands: `"info threads"`, `"backtrace"`, `"print variable"`
  - Shell commands: prefix with `!` or `shell`, e.g., `"!ls"` or `"shell pwd"`

**Example:**
```python
from gdbrpc.utils import ShellExec

# GDB command
gdb_request = ShellExec("backtrace full")

# Shell command
shell_request = ShellExec("!cat /proc/meminfo")
```

#### `Request`

Base class for all request types. Custom requests can be created by subclassing.

**Methods:**
- `__init__()`: Initializes request with unique tag ID
- `__call__(*args, **kwargs)`: Must be implemented by subclasses

#### `PostRequest`

Base class for requests with callbacks. Used for asynchronous request handling.

**Methods:**
- `__init__()`: Initializes with finish event
- `__call__(argument: Any)`: Must be implemented by subclasses
- `finish` (threading.Event): Event to signal completion

## Configuration

### Server Configuration

The server can be configured when starting:

```python
import logging
import gdbrpc

# Start with debug logging
gdbrpc.start_gdb_socket_server(
    port=20819,
    host="0.0.0.0",  # Listen on all interfaces
    logLevel=logging.DEBUG
)
```

### Client Configuration

```python
import logging
from gdbrpc import Client
from gdbrpc.utils import ShellExec

# Create client with custom log level
client = Client(
    host="localhost",
    port=20819,
    logLevel=logging.DEBUG  # Enable debug logging
)
client.connect()

# Custom timeout for specific requests
result = client.call(
    ShellExec("interrupt"),
    timeout=60  # Wait up to 60 seconds for this command
)
```

## Troubleshooting

### Server won't start

- Ensure GDB has Python support: `gdb --configuration | grep python`
- Check if port is already in use: `netstat -an | grep 20819`
- Verify firewall settings allow the connection

### Connection refused

- Verify server is running: `(gdb) gdbrpc status`
- Check host/port configuration matches between client and server
- Ensure network connectivity between client and server

### Command execution fails

- Verify GDB is in correct state (e.g., program loaded, running)
- Check command syntax is correct for your GDB version
- Review server logs for detailed error messages
- Make sure python version GDB uses is same as client


## Contributing

Contributions are welcome! Please feel free to submit pull requests or open issues for bugs and feature requests.

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

---

> [!NOTE]
> While gdbrpc was originally developed as part of the NuttX RTOS debugging tools, it is a standalone, general-purpose library that can be used with any GDB debugging session.
