# File Research: sources/os/bsd/netbsd-src/lib/libc/rpc/rpc_commondata.c

Read completely: 56 lines.

Defines shared exported RPC data: `_null_auth`, and under `_LIBC`, compatibility globals `svc_fdset` and `svc_maxfd`.

The `svc_fdset` object is a fixed 256-fd compatibility view (`__fd_set_256`) maintained by `svc_fdset.c` when the global fdset changes. This file intentionally contains common data only, not logic.
