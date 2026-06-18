# sources/test-tools/crashmonkey/code/utils/communication/ClientSocket.h

Purpose: declares the CrashMonkey AF_UNIX client socket abstraction. It provides command send and message receive methods for user tools.

Important APIs/types/functions: `ClientSocket`, `Init`, `SendCommand`, `SendMessage`, `WaitForMessage`, `CloseClient`, `socket_fd`, and `socket_address`. It is explicitly documented as not thread-safe.

Control flow: header-only declarations; implementation connects to a Unix socket and uses `BaseSocket` encoding. State/persistence behavior: one mutable file descriptor tracks connection state.

Dependencies/integration: included by `ClientCommandSender`. Risks/test signals: no copy/move controls are declared, so accidental copying could duplicate fd ownership.
