# sources/test-tools/strace/tests/netlink_sock_diag.c

Purpose: exercises send-side decoding of `NETLINK_SOCK_DIAG` requests and diagnostic messages across UNIX, NETLINK, PACKET, INET, and optional SMC families.

Important APIs, types, and helpers: `create_nl_socket(NETLINK_SOCK_DIAG)`, `sendto`, `SOCK_DIAG_BY_FAMILY`, `TCPDIAG_GETSOCK`, `TEST_SOCK_DIAG`, `unix_diag_req/msg`, `netlink_diag_req/msg`, `packet_diag_req/msg`, `inet_diag_req`, `inet_diag_req_v2`, `inet_diag_msg`, optional `smc_diag_req/msg`, `inet_pton`, `ifindex_lo`, and cookie printing macros.

Control flow: `main` checks message type and dump flags, odd/unknown family payloads in request and dump contexts, then structured request/response payloads for each supported socket family. Each `TEST_SOCK_DIAG` invocation covers family-only, family-plus-extra, exact object, and short-read decoding.

State and persistence: all payloads are synthetic and sent through a temporary sock_diag netlink fd. The file resolves constant IP addresses into in-memory structs but does not create real network connections.

Dependencies and integration points: depends on many diagnostic UAPI headers and strace xlat tables for socket families, TCP states, packet protocols, diag show flags, and cookies. Optional AF_SMC support is compile-time gated.

Risks and edge cases: diagnostic UAPI version differences, optional SMC availability, endian-sensitive port/address printing, bitmask formatting, and short-read pointer fallback are key risks.

Test signals: expected output should decode each diagnostic structure with symbolic families/states/options, show unknown family fallbacks, and finish with `+++ exited with 0 +++`.
