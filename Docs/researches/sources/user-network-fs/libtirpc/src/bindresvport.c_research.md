## sources/user-network-fs/libtirpc/src/bindresvport.c

Purpose: Implements BSD-compatible reserved-port binding for RPC clients that need privileged source ports. `bindresvport` delegates to `bindresvport_sa`.

Important APIs and control flow: On Linux, the implementation scans ports 600 through 1023, below `IPPORT_RESERVED`, while skipping entries loaded from `/etc/bindresvport.blacklist`. `load_blacklist` parses comments, whitespace, decimal or base-detected port values, and ignores out-of-range entries. `bindresvport_sa` accepts `sockaddr_in`, optionally `sockaddr_in6`, or a null address, determines the socket family with `getsockname` when needed, randomizes/rotates the static start port, binds under `port_lock`, and treats `EADDRINUSE`, `EADDRNOTAVAIL`, and similar retryable errors as signals to continue scanning.

State and persistence: Maintains static blacklist storage and a static starting port across calls. External persistence is limited to the system blacklist file and the bound socket.

Dependencies and integration: Used by `clnt_tli_create` for sockets opened by the generic client path. Relies on privilege/CAP_NET_BIND_SERVICE semantics and shared `port_lock`.

Risks and test signals: Behavior is platform-conditional and privilege-sensitive. Tests should verify blacklist parsing, concurrent calls, port wraparound, IPv4/IPv6 sockaddr updates, and no mutation beyond the port field.
