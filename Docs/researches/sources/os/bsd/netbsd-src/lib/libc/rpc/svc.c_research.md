# File Research: sources/os/bsd/netbsd-src/lib/libc/rpc/svc.c

Read completely: 815 lines.

Implements the core server-side RPC dispatcher and service registry. Transport registration uses `xprt_register()`/`xprt_unregister()` with a dynamically grown `__svc_xports` array; index `-1` is reserved for raw transports. Registered fds are mirrored into `svc_fdset.c` state.

Service registration uses a global `svc_callout` list keyed by program, version, and optionally netid. `svc_reg()` records dispatch functions and registers with local rpcbind via `rpcb_set()` when a netconfig is supplied. `svc_unreg()` removes all matching callouts and unsets rpcbind mappings. `PORTMAP` builds also include legacy `svc_register()`/`svc_unregister()` using pmap.

The reply helpers construct accepted/denied RPC replies for success, no-procedure, decode error, system error, auth error, weak auth, no-program, and version mismatch. `svc_getreq_common()` receives messages from the selected transport, authenticates via `_authenticate()`, locates the matching service callout, dispatches, or returns program/version errors. It also handles batched requests and destroys dead transports.

`rpc_control()` currently supports setting/getting `RPC_SVC_CONNMAXREC`. Reliability notes: dispatch walks `svc_head` without holding `svc_lock` in `svc_getreq_common()`, relying on broader RPC usage assumptions; `svc_unreg()` frees `sc_netid` with an incorrect size expression, though `mem_free` may ignore size depending on allocator configuration.
