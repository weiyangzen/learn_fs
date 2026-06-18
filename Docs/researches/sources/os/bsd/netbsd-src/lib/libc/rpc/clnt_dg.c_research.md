# File Research: sources/os/bsd/netbsd-src/lib/libc/rpc/clnt_dg.c

Read completely: 764 lines.

This file implements connectionless/datagram RPC clients: `clnt_dg_create` and the associated call, error, free, control, destroy, and ops functions.

Key behavior: creation validates socket info, determines send/receive buffer sizes, allocates one private block containing input/output buffers, pre-serializes the call header with an initial XID, sets the fd nonblocking, and defaults to AUTH_NONE. Calls hold a per-fd lock, increment the XID, marshal proc/auth/args, send with `sendto`, poll with a total timeout and exponential retransmit up to `RPC_MAX_BACKOFF`, match replies by XID, decode with `xdr_replymsg`, validate auth, and refresh credentials up to two times on auth errors. `clnt_dg_control` supports timeout, retry timeout, fd close policy, service address, XID, program, and version controls.

Important interactions: selected by `clnt_tli_create` for `NC_TPI_CLTS`; relies on shared `clnt_fd_lock`, `pollts`, XDR, auth ops, and `__RPC_GETXID`.

Security/reliability notes: per-fd locking serializes all concurrent calls sharing a descriptor. `CLSET_SVC_ADDR` appears to reject addresses smaller than `sockaddr_storage` and then copies `addr->len` bytes into fixed storage, which looks inverted and potentially unsafe if reachable with oversized lengths.
