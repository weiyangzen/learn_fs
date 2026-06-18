# sources/test-tools/strace/tests/net-yy-inet.c

Purpose: provides the parameterized IPv4 implementation for `strace -yy` endpoint annotation tests. It builds a loopback TCP client/server pair and verifies that descriptors are printed with local and peer addresses/ports.

Important APIs, types, and helpers: `socket`, `bind`, `getsockname`, `listen`, `connect`, `accept4`, `getpeername`, `getsockopt(SO_SNDBUF)`, `setsockopt(SOL_TCP, TCP_MAXSEG)`, `sendto`, `recvfrom`, `close`, `inet_ntop`-style socket address fields, `inode_of_sockfd`, and macro parameters such as `ADDR_FAMILY`, `SOCKADDR_TYPE`, `LOOPBACK`, `TCP_STR`, and `INPORT`.

Control flow: the file creates a loopback listener with port zero, obtains the assigned port, connects a second socket, accepts the connection, verifies names/options, sends and receives a short payload, and closes descriptors. Macro definitions make the same body reusable for IPv6 through `net-yy-inet6.c`.

State and persistence: all state is ephemeral TCP socket state on loopback. The assigned listener/client ports and inode-derived fd annotations are runtime values used in expected output; no filesystem state persists.

Dependencies and integration points: depends on loopback networking, `/proc/self/fd/`, TCP socket support, and strace `-yy` formatting. The file is directly included by the IPv6 wrapper after redefining address-family macros.

Risks and edge cases: loopback availability, kernel option defaults, port allocation, and macro correctness are important. The test avoids fixed ports but still relies on deterministic local endpoint rendering.

Test signals: expected output shows `<TCP:[127.0.0.1:port]>` and connected `<TCP:[src->dst]>` annotations, successful option calls, payload transfer, clean closes, and the exit marker.
