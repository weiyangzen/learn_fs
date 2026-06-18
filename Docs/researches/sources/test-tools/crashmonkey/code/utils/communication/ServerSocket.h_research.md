# sources/test-tools/crashmonkey/code/utils/communication/ServerSocket.h

Purpose: declares the CrashMonkey harness server socket abstraction. It accepts command messages and sends command replies.

Important APIs/types/functions: `ServerSocket`, `Init`, `SendCommand`, `SendMessage`, `WaitForMessage`, `TryForMessage`, `CloseClient`, `CloseServer`, `server_socket`, `client_socket`, and `socket_address`.

Control flow: declarations only; `.cpp` handles poll/accept/read/write. State/persistence behavior: one listening fd and one active client fd represent state, with socket-file cleanup on destruction.

Dependencies/integration: included by harness code outside this subset. Risks/test signals: non-thread-safe, single-client design; tests in this subset do not exercise server behavior.
