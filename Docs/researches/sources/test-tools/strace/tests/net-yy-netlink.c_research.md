# sources/test-tools/strace/tests/net-yy-netlink.c

Purpose: checks `-yy`/socket descriptor annotation for netlink sockets, especially transition from unbound socket inode display to protocol/pid-aware `NETLINK:[SOCK_DIAG:pid]` display.

Important APIs, types, and helpers: `socket(AF_NETLINK, SOCK_RAW, NETLINK_SOCK_DIAG)`, `bind`, `getsockname`, `close`, `struct sockaddr_nl`, `inode_of_sockfd`, `tail_memdup`, and configurable `PRINT_SOCK` formatting macros.

Control flow: `main` creates a netlink socket, records the inode when annotation is enabled, binds the socket to the process pid, calls `getsockname`, closes it, and prints expected fd annotations for unbound and bound states.

State and persistence: socket state is transient. The bind uses `getpid()` as `nl_pid`; no filesystem or persistent kernel state is left after close.

Dependencies and integration points: requires `/proc/self/fd/`, `NETLINK_SOCK_DIAG`, Linux netlink headers, and strace fd annotation modes. `PRINT_SOCK` allows the same logic to support different expected annotation levels.

Risks and edge cases: pid namespace translation, kernel netlink pid assignment behavior, and annotation mode changes can alter output. Binding may fail on systems lacking the protocol, leading to skip.

Test signals: output should show socket creation, bind, getsockname, close, and the descriptor annotation selected by `PRINT_SOCK`, followed by the normal exit marker.
