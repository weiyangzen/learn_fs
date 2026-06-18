<!-- BEGIN_FILE_RESEARCH: sources/test-tools/strace/src/netlink_sock_diag.c -->
# sources/test-tools/strace/src/netlink_sock_diag.c

Purpose: top-level `NETLINK_SOCK_DIAG` payload dispatcher across socket address families.

Important APIs/types/functions: `decode_netlink_sock_diag`, local `decode_family`, `diag_decoders`, and decoder pairs for AF_UNIX, AF_INET/AF_INET6, AF_NETLINK, AF_PACKET, and AF_SMC.

Control flow: skips `NLMSG_DONE`, reads the first family byte, selects request or response decoder based on `NLM_F_REQUEST`, and falls back to printing family plus raw data when no decoder exists.

State and persistence behavior: no persistent state.

Dependencies and integration points: invoked from `netlink.c`; depends on `netlink_sock_diag.h`, addrfams xlats, and family-specific diag files.

Risks: family dispatch assumes the first byte is the family and that `NLM_F_REQUEST` accurately distinguishes request from response. New sock_diag families need table entries.

Test signals: request and response messages for each registered family, unknown families, short buffers, `NLMSG_DONE`, and missing decoder fallback.
<!-- END_FILE_RESEARCH: sources/test-tools/strace/src/netlink_sock_diag.c -->
