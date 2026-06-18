# sources/test-tools/crashmonkey/code/utils/communication/ClientCommandSender.cpp

Purpose: implements a one-shot command client for harness control operations. It connects, sends one command, waits for one response, and reports whether the expected response arrived.

Important APIs/types/functions: `ClientCommandSender` constructor, `Run`, `ClientSocket::Init`, `SendCommand`, `WaitForMessage`, and `SocketMessage`. It stores socket path, command to send, command expected back, and a `ClientSocket`.

Control flow: `Run` returns -1 if connect fails, -2 if send fails, -3 if receive fails, otherwise returns boolean negation of `ret.type == return_command` so success is 0 and wrong reply is 1.

State/persistence behavior: owns only transient socket connection state through `ClientSocket`. Dependencies/integration: used by begin/end log/test shims and checkpoint API.

Risks/test signals: the wrong-reply path loses the actual command received; no retry or timeout is implemented at this layer; lifecycle is one command per instance.
