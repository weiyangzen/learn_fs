<!-- BEGIN_FILE_RESEARCH: sources/user-network-fs/libtirpc/src/authgss_prot.c -->
# sources/user-network-fs/libtirpc/src/authgss_prot.c

Purpose: XDR and GSS helper routines for RPCSEC_GSS credentials, init tokens, and protected data bodies.

Important APIs, types, and functions: Exports `xdr_rpc_gss_buf`, `xdr_rpc_gss_cred`, `xdr_rpc_gss_init_args`, `xdr_rpc_gss_init_res`, `xdr_rpc_gss_wrap_data`, `xdr_rpc_gss_unwrap_data`, `xdr_rpc_gss_data`, and debug helpers `gss_log_debug`, `gss_log_status`, `gss_log_hexdump`.

Control flow: Encode paths serialize GSS buffers and credentials, or marshal sequence+payload then compute MIC for integrity or wrap/encrypt for privacy. Decode paths read integrity/privacy bodies, verify MIC/QOP or unwrap confidentiality, decode sequence+payload from a memory XDR stream, and check sequence number.

State and persistence behavior: No persistent module state except debug globals from libtirpc. GSS buffers decoded by XDR/GSS helpers require normal release/free handling by callers.

Dependencies and integration points: Used by `auth_gss.c` for RPCSEC_GSS init and per-call wrap/unwrap. Depends on GSSAPI and XDR.

Risks: Slack-based max sizes are permissive and must not allow unbounded allocation on hostile inputs; decode uses `(u_int)-1` for some buffers. Sequence and QOP checks are security-critical. Debug hexdumps can expose sensitive token data when high debug logging is enabled.

Test signals: No direct unit test in this subset; covered by GSS-enabled builds and RPCSEC_GSS integration clients.
<!-- END_FILE_RESEARCH: sources/user-network-fs/libtirpc/src/authgss_prot.c -->
