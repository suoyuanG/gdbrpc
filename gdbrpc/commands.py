############################################################################
# nxgdb/gdbrpc.py
#
# SPDX-License-Identifier: Apache-2.0
#
# Licensed to the Apache Software Foundation (ASF) under one or more
# contributor license agreements.  See the NOTICE file distributed with
# this work for additional information regarding copyright ownership.  The
# ASF licenses this file to you under the Apache License, Version 2.0 (the
# "License"); you may not use this file except in compliance with the
# License.  You may obtain a copy of the License at
#
#   http://www.apache.org/licenses/LICENSE-2.0
#
# Unless required by applicable law or agreed to in writing, software
# distributed under the License is distributed on an "AS IS" BASIS, WITHOUT
# WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.  See the
# License for the specific language governing permissions and limitations
# under the License.
#
############################################################################

import argparse
import logging
import os

import gdb
import gdbrpc
import psutil

from .server import Server

g_socket_server: Server = None


def start_gdb_socket_server(
    port: int = 20819, host: str = "localhost", logLevel=logging.INFO
):
    """Start the GDB socket server"""
    global g_socket_server

    if g_socket_server and g_socket_server.running:
        print(
            f"GDB Socket Server already running on {g_socket_server.host}:{g_socket_server.port}"
        )
        return

    g_socket_server = Server(port, host, logLevel)
    g_socket_server.start()


def stop_gdb_socket_server():
    """Stop the GDB socket server"""
    global g_socket_server

    if g_socket_server:
        g_socket_server.stop()
        g_socket_server = None


def get_gdb_socket_server_status():
    """Get server status"""
    if g_socket_server and g_socket_server.running:
        return {
            "running": True,
            "host": g_socket_server.host,
            "port": g_socket_server.port,
            "clients": len(g_socket_server.clients),
        }
    else:
        return {"running": False}


class StartSocketServer(gdb.Command):
    """Start GDB socket server command"""

    def get_argparser(self):
        parser = argparse.ArgumentParser(description="Start GDB socket server")
        parser.add_argument("--port", type=int, default=20819, help="Port to listen on")
        parser.add_argument("--host", default="localhost", help="Host to bind to")
        parser.add_argument(
            "--debug", action="store_true", default=False, help="Enable debug logging"
        )
        return parser

    def __init__(self):
        super().__init__("gdbrpc start", gdb.COMMAND_USER)
        self.parser = self.get_argparser()

    def invoke(self, arg, from_tty):
        args = gdb.string_to_argv(arg)
        if not args:
            port = 20819
            host = "localhost"
            logLevel = logging.INFO
        else:
            try:
                args = self.parser.parse_args(args)
                port = args.port
                host = args.host
                logLevel = logging.DEBUG
            except SystemExit:
                return

        start_gdb_socket_server(port, host, logLevel)


class StopSocketServer(gdb.Command):
    """Stop GDB socket server command"""

    def __init__(self):
        super().__init__("gdbrpc stop", gdb.COMMAND_USER)

    def invoke(self, arg, from_tty):
        stop_gdb_socket_server()


class SocketServerStatus(gdb.Command):
    """Get socket server status command"""

    def __init__(self):
        super().__init__("gdbrpc status", gdb.COMMAND_USER)

    @classmethod
    def get_memory_usage(cls):
        process = psutil.Process(os.getpid())
        memory_info = process.memory_info()
        return {
            "rss": memory_info.rss / 1024 / 1024,  # MB
            "vms": memory_info.vms / 1024 / 1024,  # MB
            "threads": len(process.threads()),
        }

    def invoke(self, arg, from_tty):
        status = get_gdb_socket_server_status()
        memory = self.get_memory_usage()

        if status["running"]:
            print("Socket Server Status:")
            print("  Running: Yes")
            print(f"  Host: {status['host']}")
            print(f"  Port: {status['port']}")
            print(f"  Connected Clients: {status['clients']}")
        else:
            print("Socket Server Status: Not running")
        print(f"  Memory Usage: {memory['rss']:.1f} MB RSS, {memory['vms']:.1f} MB VMS")
        print(f"  Active Threads: {memory['threads']}")


# !NOTE: This command is under development and may not work as expected
class StartSocketClient(gdb.Command):
    """Connect to GDB socket server"""

    def get_argparser(self):
        parser = argparse.ArgumentParser(description="Start GDB socket client")
        parser.add_argument(
            "--port", type=int, default=20819, help="Port to connect to"
        )
        parser.add_argument("--host", default="localhost", help="Host to connect to")
        return parser

    def __init__(self):
        super().__init__("gdbrpc connect", gdb.COMMAND_USER)
        self.parser = self.get_argparser()

    def invoke(self, arg, from_tty):
        args = gdb.string_to_argv(arg)
        if not args:
            port = 20819
            host = "localhost"
        else:
            try:
                args = self.parser.parse_args(args)
                port = args.port
                host = args.host
            except SystemExit:
                return

        client = gdbrpc.ClientCLI(host, port)
        client.start()
