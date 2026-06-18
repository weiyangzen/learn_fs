# File Research: sources/os/bsd/netbsd-src/lib/libc/rpc/rpc_prot.c

Read completely: 349 lines.

Implements core RPC protocol XDR and reply-to-error mapping. XDR helpers include `xdr_opaque_auth()`, `xdr_des_block()`, `xdr_accepted_reply()`, `xdr_rejected_reply()`, `xdr_replymsg()`, and `xdr_callhdr()`.

`xdr_accepted_reply()` handles `SUCCESS` by dispatching to the result XDR callback and encodes version bounds for `PROG_MISMATCH`. `xdr_rejected_reply()` handles RPC-version mismatch and auth errors. `_seterr_reply()` maps decoded reply statuses into `struct rpc_err`, including version ranges and auth failure reasons.

This file is shared by client and server code. It is protocol-level, not transport-specific.
