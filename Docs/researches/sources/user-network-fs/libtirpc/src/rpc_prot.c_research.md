<!-- BEGIN_FILE_RESEARCH: sources/user-network-fs/libtirpc/src/rpc_prot.c -->
# sources/user-network-fs/libtirpc/src/rpc_prot.c

Purpose: common RPC protocol XDR and reply-to-error mapping helpers shared by clients and servers.

Important APIs and functions: `xdr_opaque_auth()`, `xdr_des_block()`, `xdr_accepted_reply()`, `xdr_rejected_reply()`, `xdr_replymsg()`, `xdr_callhdr()`, and `_seterr_reply()`. Static `accepted()` and `rejected()` translate protocol accept/reject statuses into `enum clnt_stat` values in `struct rpc_err`.

Control flow: reply XDR uses a discriminator table to decode/encode `MSG_ACCEPTED` versus `MSG_DENIED`. Accepted replies serialize verifier and accept status, then either call the embedded result XDR procedure for `SUCCESS`, encode low/high versions for `PROG_MISMATCH`, or accept terminal error statuses with no payload. Rejected replies encode RPC version ranges or authentication reasons. `_seterr_reply()` handles the success fast path and fills version or auth details when appropriate.

State and persistence: no mutable file-local state. It references global `_null_auth` declared elsewhere but only as an external symbol.

Dependencies and integration points: used by transport reply code such as `svc_dg_reply()` and raw/connection transports, and by client code to interpret server replies. Depends on public RPC structs and XDR.

Risks: `xdr_callhdr()` only supports `XDR_ENCODE`; callers using decode/free get `FALSE`. Unknown accept/reject discriminants collapse to generic failure. Result XDR callbacks must be valid for `SUCCESS` replies.

Test signals: encode/decode reply messages for success, program mismatch, auth error, RPC mismatch, garbage args, and unknown statuses; verify `_seterr_reply()` populates `re_vers` and `re_why`; and validate `xdr_callhdr()` emits the expected static call header.
<!-- END_FILE_RESEARCH: sources/user-network-fs/libtirpc/src/rpc_prot.c -->
