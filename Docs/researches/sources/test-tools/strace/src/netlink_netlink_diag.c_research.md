<!-- BEGIN_FILE_RESEARCH: sources/test-tools/strace/src/netlink_netlink_diag.c -->
# sources/test-tools/strace/src/netlink_netlink_diag.c

Purpose: decodes AF_NETLINK sock_diag request and response payloads.

Important APIs/types/functions: `decode_netlink_diag_req`, `decode_netlink_diag_msg`, `decode_netlink_diag_groups`, `decode_netlink_diag_ring`, `decode_netlink_diag_flags`, and `netlink_diag_msg_nla_decoders`.

Control flow: request decoding prints `netlink_diag_req` including protocol, inode, show flags, and cookie. Response decoding prints `netlink_diag_msg` fields, then aligned `NETLINK_DIAG_*` attributes for meminfo, group masks, RX/TX rings, and socket flags.

State and persistence behavior: no durable state. Group attributes are interpreted in current tracee word size.

Dependencies and integration points: registered through `netlink_sock_diag.c`; depends on `<linux/netlink_diag.h>`, shared `nlattr` decoders, `netlink_protocols`, `socktypes`, and generated diag xlat tables.

Risks: group mask element width varies with personality word size. Unknown protocols and newly added attributes fall back to generic hex if xlat/decoder tables lag.

Test signals: cover `NDIAG_PROTO_ALL`, protocol-specific requests, group arrays for 32/64-bit personalities, ring attributes, flags attributes, and short messages.
<!-- END_FILE_RESEARCH: sources/test-tools/strace/src/netlink_netlink_diag.c -->
