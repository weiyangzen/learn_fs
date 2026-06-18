<!-- BEGIN_FILE_RESEARCH: sources/user-network-fs/libtirpc/src/svc_dg.c -->
# sources/user-network-fs/libtirpc/src/svc_dg.c

Purpose: connectionless/datagram server transport implementation with optional duplicate request cache for at-most-once reply behavior.

Important APIs and functions: `svc_dg_create()` creates/registers a datagram `SVCXPRT`; transport ops include `svc_dg_recv()`, `svc_dg_reply()`, `svc_dg_getargs()`, `svc_dg_freeargs()`, `svc_dg_destroy()`, `svc_dg_stat()`, and `svc_dg_control()`. Cache APIs include `svc_dg_enablecache()`, `cache_get()`, and `cache_set()`. Packet-info helpers are `svc_dg_enable_pktinfo()` and `svc_dg_valid_pktinfo()`.

Control flow: creation derives socket metadata, computes send/receive buffer size, allocates `SVCXPRT`, extension, private `svc_dg_data`, and an aligned XDR buffer, records local address via `getsockname`, enables packet-info cmsgs for IPv4/IPv6, installs ops, and registers the transport. Receive uses `recvmsg`, saves remote address, preserves valid IP_PKTINFO/IPV6_PKTINFO control data for the reply, decodes an RPC call with `xdr_callmsg`, and returns cached replies immediately for duplicate requests. Reply encodes an RPC reply header, temporarily moves success result encoding through `SVCAUTH_WRAP`, sends with the preserved destination control message, and saves the reply in cache on success. Argument decode uses `SVCAUTH_UNWRAP`.

State and persistence: per-transport private state stores XDR stream, I/O buffer, current xid, verifier storage, cmsg buffer, and optional cache. The cache has a hash table plus FIFO victim array and entries keyed by xid/prog/vers/proc/client address; `dupreq_lock` guards cache access.

Dependencies and integration points: used by `svc_generic.c` and legacy `svcudp_create`. Integrates with `svc.c` registration/dispatch, `xdr_callmsg`, `xdr_replymsg`, auth wrap/unwrap, socket `recvmsg`/`sendmsg`, and `rpc_generic.c` address helpers.

Risks: cache entries allocate copied remote addresses but victim replacement reuses nodes without visibly freeing old `cache_addr.buf`, creating leak risk. Packet-info validation only accepts a single cmsg and clears interface index before reply. `svc_dg_control()` is a stub. Datagram transport is sensitive to buffer sizing and message truncation.

Test signals: datagram request/reply round trip, duplicate xid replay returns cached reply without dispatch, cache eviction, auth wrap/unwrap with GSS, IPv4 and IPv6 packet-info replies to aliased addresses, malformed/truncated RPC calls, EINTR retry in receive, destruction cleanup, and cache enable called twice.
<!-- END_FILE_RESEARCH: sources/user-network-fs/libtirpc/src/svc_dg.c -->
