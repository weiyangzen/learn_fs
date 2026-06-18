# sources/test-tools/crashmonkey/code/utils/communication/ClientCommandSender.h

Purpose: declares the one-shot command sender used by CrashMonkey user tools. It wraps the lower-level `ClientSocket` into a simple send/expect API.

Important APIs/types/functions: class `ClientCommandSender`, constructor taking socket address, send command, and expected receive command, `Run`, `socket_address`, `send_command`, `return_command`, and `conn`.

Control flow: no implementation here; `Run` handles connect/send/wait in the `.cpp`. State/persistence behavior: stores immutable command parameters and one client socket object.

Dependencies/integration: depends on `ClientSocket.h` and `SocketUtils.h`; used by command-line shims and `actions.cpp`. Risks/test signals: the class only supports command messages and cannot send payload-bearing requests without extending BaseSocket and SocketMessage handling.
