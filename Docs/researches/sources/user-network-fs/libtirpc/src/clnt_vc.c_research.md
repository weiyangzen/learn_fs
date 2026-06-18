## sources/user-network-fs/libtirpc/src/clnt_vc.c

Purpose: Implements connection-oriented RPC `CLIENT` transport for TCP/local stream-style netconfig entries using XDR record streams.

Important APIs and control flow: `clnt_vc_create` allocates `CLIENT` and `ct_data`, creates/reuses an fd lock, connects the socket when needed, copies the remote `netbuf`, pre-marshals a static call header with a process-global `disrupt` component in the XID, and initializes `xdrrec_create` with `read_vc`/`write_vc`. `clnt_vc_call` serializes a call into the record stream, supports batched calls when no results and zero timeout are requested, then skips records until the matching XID is decoded. It validates auth, unwraps results, and may refresh credentials. `clnt_vc_control` exposes timeout, fd, address, XID, program, and version controls.

State and persistence: Per-client state tracks fd ownership, timeout, remote address, cached error, pre-marshalled header, and XDR record stream. Shared static fd locks serialize handles on the same fd.

Dependencies and integration: Selected by `clnt_tli_create` for connection-oriented netconfig semantics. Uses poll/read/write, XDR records, auth APIs, `ops_lock`, `disrupt_lock`, and optional GSS.

Risks and test signals: Full-call fd locking limits concurrency. Tests should cover batching, timeout propagation to `read_vc`, mismatched XID skipping, control mutation of header fields, destroy pending waits, and short writes/EOF.
