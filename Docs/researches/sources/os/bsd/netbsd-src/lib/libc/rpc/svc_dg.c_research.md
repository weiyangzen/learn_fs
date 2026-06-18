# File Research: sources/os/bsd/netbsd-src/lib/libc/rpc/svc_dg.c

Read completely: 626 lines.

Implements connectionless/datagram server transports. `svc_dg_create()` derives socket info from the fd, chooses send/receive sizes, allocates an `SVCXPRT`, datagram-private state, an aligned RPC buffer, an XDR memory stream, local address storage, and registers the transport.

Transport ops implement receive, reply, argument decode/free, destroy, status, and no-op control. `svc_dg_recv()` reads with `recvfrom()`, stores the remote address, decodes an RPC call with `xdr_callmsg()`, and checks the duplicate-request cache. `svc_dg_reply()` encodes `xdr_replymsg()`, sends with `sendto()`, and stores the reply in cache when enabled.

The duplicate-request cache (`svc_dg_enablecache()`, `cache_get()`, `cache_set()`) is a FIFO hash table keyed by xid, program, version, procedure, and remote address. Duplicate requests get the cached reply resent without redispatch. Cache state is protected by `dupreq_lock`.

Reliability notes: cache replacement reuses cached reply buffers but allocates a fresh copy of the remote address each set; replacement paths should be reviewed for old address-buffer ownership. `xp_rtaddr.len` is also used as allocation size for freeing, while `maxlen` is used in destroy.
