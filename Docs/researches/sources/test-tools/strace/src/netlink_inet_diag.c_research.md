<!-- BEGIN_FILE_RESEARCH: sources/test-tools/strace/src/netlink_inet_diag.c -->
# sources/test-tools/strace/src/netlink_inet_diag.c

Purpose: decodes AF_INET/AF_INET6 sock_diag requests and responses, including legacy inet_diag requests, v2 requests, TCP metrics, ULP info, and nested diagnostic attributes.

Important APIs/types/functions: `print_inet_diag_sockid`, `decode_inet_diag_req`, `decode_inet_diag_msg`, bytecode decoders, `decode_tcpvegas_info`, `decode_tcp_dctcp_info`, `decode_tcp_bbr_info`, `decode_tcp_md5sig`, TLS/MPTCP ULP decoders, BPF storage decoders, and `decode_diag_sockopt`.

Control flow: request decoding chooses legacy `inet_diag_req` for `TCPDIAG_GETSOCK`/`DCCPDIAG_GETSOCK` and `inet_diag_req_v2` otherwise, then decodes request attributes. Response decoding prints `inet_diag_msg` fields and then aligned `INET_DIAG_*` attributes with nested dispatch for ULP, BPF storage, socket arrays, congestion info, and sockopt bitfields.

State and persistence behavior: no durable state; all work is tracee-memory fetch plus output formatting. Sparse bitfields are omitted in abbrev mode unless nonzero.

Dependencies and integration points: used by `netlink_sock_diag.c`; depends on Linux `inet_diag`, `tcp`, `tls`, `mptcp`, shared `nlattr` helpers, socket address printers, xlat tables, and `print_inet_diag_sockid` exported through `netlink_sock_diag.h`.

Risks: many structures are kernel-version dependent. Optional field printing via payload length must track ABI additions; unsupported `INET_DIAG_INFO` remains raw. Bytecode and nested attributes need correct length alignment to avoid misleading output.

Test signals: cover legacy/v2 requests, IPv4 and IPv6 sockids, bytecode host/mark/dev conditions, all implemented response attributes, TLS and MPTCP ULP nests, BPF storage, sockopt nonzero/abbrev behavior, short payloads, and unknown attributes.
<!-- END_FILE_RESEARCH: sources/test-tools/strace/src/netlink_inet_diag.c -->
