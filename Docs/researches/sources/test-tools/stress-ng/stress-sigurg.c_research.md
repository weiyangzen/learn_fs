# sources/test-tools/stress-ng/stress-sigurg.c

Purpose: implements the `sigurg` network stressor, generating SIGURG from TCP out-of-band data sent by a server and consumed by a client-side SIGURG handler.

Important APIs/types/functions: `stress_sigurg_handler`, `stress_sigurg_client`, `stress_send_error`, `stress_sigurg_server`, `stress_sigurg`, `socket`, `connect`, `bind`, `listen`, `accept`, `send(..., MSG_OOB)`, `recv(..., MSG_OOB)`, `ioctl(SIOCATMARK)`, `fcntl(F_SETOWN)`, `stress_net_reserve_ports`, and `stress_net_sockaddr_if_set`.

Control flow: the worker reserves a per-instance TCP port, installs SIGURG, synchronizes start, then forks a client. The client repeatedly connects to the server, sets itself as socket owner, loops checking the urgent mark and reading normal data while the handler receives out-of-band bytes. The parent server binds/listens, accepts connections, sends one-byte MSG_OOB payloads until stop or send error, then closes sockets, kills/reaps the client, and releases the port.

State and persistence behavior: global state holds args and the current client socket fd used by the SIGURG handler. Network sockets and reserved port state are transient and released at exit.

Dependencies and integration points: registered as `CLASS_SIGNAL | CLASS_NETWORK | CLASS_OS`, verify none. It depends on TCP/IP socket support, `SIOCATMARK`, `F_SETOWN`, stress-ng network address helpers, port reservation, and SIGCHLD handling.

Risks and test signals: network behavior is timing-sensitive and can be affected by port conflicts, socket buffer pressure, and platform OOB semantics. Signals include connection retries exceeding limit, unexpected send/recv/ioctl failures, missing bogo increments from handler, or leaked reserved ports.
