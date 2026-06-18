# sources/user-network-fs/impacket/impacket/examples/ntlmrelayx/utils/tcpshell.py

Purpose: provides a minimal local TCP shell endpoint used by interactive relay attacks. Each `TcpShell` instance listens on localhost and exposes accepted socket file objects as stdin/stdout.

Important APIs and control flow: module-level `port` starts at 11000. `TcpShell.__init__()` assigns the current global port to the instance and increments the global for the next shell. `listen()` creates an IPv4 TCP socket, binds `127.0.0.1:self.port`, calls `listen(0)`, blocks in `accept()`, then creates text-mode file objects with `makefile("r")` and `makefile("w")`. `close()` closes stdout, stdin, and the accepted connection.

State and persistence: state is process-local only: the global port counter plus per-instance socket connection and file handles. No disk persistence.

Dependencies and integration: depends only on Python `socket`. It integrates with attack modules that need an operator-facing interactive channel after successful relay.

Risks and test signals: the listening socket object is local to `listen()` and is not explicitly closed after accept. The global port increment is not thread-safe, and port collisions are possible across processes. Tests should cover sequential port allocation, bind/listen/accept behavior, stdin/stdout file creation, close idempotency expectations, and failure when the selected port is already in use.
