# sources/test-tools/crashmonkey/code/utils/communication/ClientSocket.cpp

Purpose: implements a simple AF_UNIX stream client socket for CrashMonkey control communication.

Important APIs/types/functions: constructor, destructor, `Init`, `SendCommand`, `SendMessage`, `WaitForMessage`, `CloseClient`, `socket`, `connect`, `close`, `sockaddr_un`, and `BaseSocket`.

Control flow: `Init` creates a local stream socket and connects to the configured path. `SendCommand` wraps a command into `SocketMessage`; `SendMessage` delegates encoding to `BaseSocket`; `WaitForMessage` delegates decoding; `CloseClient` closes and resets the descriptor.

State/persistence behavior: owns one socket fd and immutable socket address. No durable state is changed. Dependencies/integration: used by `ClientCommandSender`.

Risks/test signals: `strcpy` into `sun_path` has no length guard, destructor closes `-1` harmlessly but may double-close if `CloseClient` was called and fd reused elsewhere, and no connection timeout exists.
