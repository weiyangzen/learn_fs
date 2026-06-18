# sources/test-tools/crashmonkey/code/utils/communication/ServerSocket.cpp

Purpose: implements the harness-side AF_UNIX server socket for receiving CrashMonkey control commands and sending acknowledgements.

Important APIs/types/functions: `ServerSocket`, `Init`, `SendCommand`, `SendMessage`, `WaitForMessage`, `TryForMessage`, `CloseClient`, `CloseServer`, `socket`, `bind`, `listen`, `poll`, `accept`, `unlink`, and `BaseSocket`. `TryForMessage` uses a 25 ms poll timeout.

Control flow: `Init` creates a nonblocking local stream socket, binds it to the configured path, and listens. `WaitForMessage` blocks in `poll`, accepts one client, reads one message, and leaves `client_socket` open for response. `TryForMessage` is the nonblocking variant. Send methods write to the accepted client, and close methods tear down fds.

State/persistence behavior: owns server and current client descriptors and unlinks the socket pathname in the destructor. Dependencies/integration: used by the harness control loop.

Risks/test signals: only one client at a time is supported, stale socket files before bind are not removed, `strcpy` can overflow `sun_path`, and caller must close each client before accepting another.
