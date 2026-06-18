<!-- BEGIN_FILE_RESEARCH: sources/test-tools/strace/tests/ip_mreq.c -->
# sources/test-tools/strace/tests/ip_mreq.c

Purpose: Tests decoding of IPv4 and IPv6 multicast membership socket options using `struct ip_mreq` and `struct ipv6_mreq`.

Important APIs/types/functions: Uses `inet_pton`, `socket`, `setsockopt`, `ifindex_lo`, `IP_ADD_MEMBERSHIP`, `IP_DROP_MEMBERSHIP`, `IPV6_ADD_MEMBERSHIP`, `IPV6_DROP_MEMBERSHIP`, `IPV6_JOIN_ANYCAST`, and `IPV6_LEAVE_ANYCAST`.

Control flow: Builds IPv4 and IPv6 multicast request structures, opens an IPv4 datagram socket on fd 0, then for each option tests negative length, one-byte-short length, faulting optval, exact structure length, and `INT_MAX` oversized length.

State/persistence behavior: The test may join/drop multicast groups on the temporary socket, but all state is process/socket scoped and disappears at exit. It closes fd 0 before opening the socket to stabilize printed fd values.

Dependencies: Requires IPv4 and IPv6 multicast constants plus loopback interface lookup. It skips when host headers do not expose required options or `lo` is unavailable.

Integration points: Validates sockopt structure decoders for IPv4 addresses, IPv6 addresses, interface indexes, and exact/oversized length behavior.

Risks: Network namespace configuration and IPv6 support can affect availability. Interface-index string output is environment-dependent through `IFINDEX_LO_STR`.

Test signals: Expected output includes pointer failures, decoded `inet_addr`/`inet_pton` structures, loopback ifindex, and final exit.

Source read signal: complete file read for this research pass; file size 142 line(s), 3834 byte(s).
<!-- END_FILE_RESEARCH: sources/test-tools/strace/tests/ip_mreq.c -->
