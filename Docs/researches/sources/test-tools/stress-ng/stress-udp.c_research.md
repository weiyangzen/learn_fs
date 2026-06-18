## sources/test-tools/stress-ng/stress-udp.c

Purpose: Implements `udp`, a verified datagram client/server stressor for IPv4/IPv6 UDP and optional UDP-Lite/GRO.

Important APIs/types/functions: `stress_udp_info`, `stress_udp`, `stress_udp_client`, and `stress_udp_server`; options cover domain, interface, port, max size, UDP-Lite, and UDP-GRO. Uses `socket`, `bind`, `sendto`, `recvfrom`, `setsockopt`, `getsockopt`, `ioctl(SIOCINQ/SIOCOUTQ)`, fork, and signal handlers.

Control flow: parent reserves a per-instance port and forks a client. The child repeatedly creates a datagram socket, configures UDP-Lite checksum coverage and optional GRO/cork/encap/no-check/segment probes, then sends buffers whose first bytes encode the child PID. The parent binds, receives datagrams, verifies the embedded PID, and increments bogo operations.

State and persistence: port reservation is per run; AF_UNIX paths, when supported by helper address construction, are unlinked; child is killed and reaped on exit.

Dependencies/integration: uses core networking, affinity, signal, and killpid helpers plus Linux UDP socket options when present.

Risks: network namespaces, packet filters, ENOBUFS/ENOMEM, unsupported UDP-Lite/domain combinations, or fork failure affect behavior; verification is content-based but minimal.

Test signals: `VERIFY_ALWAYS`; primary correctness signal is server PID validation and clean child exit.
