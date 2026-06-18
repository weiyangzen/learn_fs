<!-- BEGIN_FILE_RESEARCH: sources/test-tools/strace/src/netlink_smc_diag.c -->
# sources/test-tools/strace/src/netlink_smc_diag.c

Purpose: decodes AF_SMC sock_diag request and response payloads, including SMC connection, link group, DMB, fallback, and shutdown attributes.

Important APIs/types/functions: `decode_smc_diag_req`, `decode_smc_diag_msg`, `decode_smc_diag_conninfo`, `decode_smc_diag_lgrinfo`, `decode_smc_diag_dmbinfo`, `decode_smc_diag_fallback`, and `smc_diag_msg_nla_decoders`.

Control flow: request decoding prints `smc_diag_req` with extended flags and an AF_INET sockid. Response decoding prints `smc_diag_msg` state, mode, shutdown, sockid, uid, and inode, then aligned `SMC_DIAG_*` attributes. Optional newer DMB extended gid fields are printed only when present.

State and persistence behavior: no durable state.

Dependencies and integration points: registered in `netlink_sock_diag.c`; uses `<linux/smc_diag.h>`, shared inet sockid printing, `nlattr`, and SMC generated xlats.

Risks: SMC headers have evolved and some fallback reasons are from non-UAPI kernel headers, so xlat staleness is likely. AF_SMC uses AF_INET sock address fields, which is easy to mis-handle.

Test signals: AF_SMC request/response traces with conninfo, lgrinfo, shutdown, DMB old/new lengths, fallback reasons, short payloads, and unknown attributes.
<!-- END_FILE_RESEARCH: sources/test-tools/strace/src/netlink_smc_diag.c -->
