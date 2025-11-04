############################################################################
# gdbrpc/cli.py
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

import logging

from gdbrpc.client import Client
from gdbrpc.utils import ShellExec


class ClientCLI(Client):
    def __init__(self, host, port):
        super().__init__(host, port, logLevel=logging.WARNING)

    def _show_command_help(self):
        print("Welcome to the GDB Remote Protocol Client")
        print("Type `exit` or `quit` to disconnect.")
        print("Type `help` to show this help message.")
        print("If you need `interrupt` command to stop the target, use Ctrl+C.")

    def _loop(self):
        print("gdb> ", end="", flush=True)
        while True:
            try:
                command = input().strip()
                if not command:
                    continue
                if command.lower() in ("exit", "quit"):
                    self.disconnect()
                    break
                if command.lower() == "help":
                    self._show_command_help()
                    print("gdb> ", end="", flush=True)
                    continue
                print(self.call(ShellExec(command)))
                print("gdb> ", end="", flush=True)
            except KeyboardInterrupt:
                print("")
                self.call(ShellExec("interrupt"))
                print("gdb> ", end="", flush=True)
            except EOFError:
                self.disconnect()

    def start(self):
        assert self.connect()
        self._show_command_help()
        self._loop()
