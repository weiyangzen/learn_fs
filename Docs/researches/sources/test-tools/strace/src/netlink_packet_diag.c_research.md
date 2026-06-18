<!-- BEGIN_FILE_RESEARCH: sources/test-tools/strace/src/netlink_packet_diag.c -->
# sources/test-tools/strace/src/netlink_packet_diag.c

Purpose: decodes AF_PACKET sock_diag requests and response attributes.

Important APIs/types/functions: `decode_packet_diag_req`, `decode_packet_diag_msg`, `decode_packet_diag_info`, multicast list/ring/filter decoders, and `packet_diag_msg_nla_decoders`.

Control flow: request decoding prints family, protocol, inode, show flags, and cookie. Response decoding prints `packet_diag_msg`, then decodes `PACKET_DIAG_*` attributes for socket info, multicast list arrays, RX/TX rings, fanout, uid, meminfo, and classic BPF filters.

State and persistence behavior: no persistent state; filter attributes are printed as socket filter programs with an unsigned-short instruction-count guard.

Dependencies and integration points: registered in `netlink_sock_diag.c`; uses `nlattr`, `print_sock_fprog`, `print_ifindex`, ethernet protocol and packet xlat tables.

Risks: AF_PACKET protocol support is documented as currently zero-only in the request path. Multicast address length is capped to the embedded address array; longer kernel formats would need updates.

Test signals: AF_PACKET request/response dumps with info, mclist, rings, fanout, meminfo, uid, valid/invalid filter lengths, short messages, and unknown attributes.
<!-- END_FILE_RESEARCH: sources/test-tools/strace/src/netlink_packet_diag.c -->
