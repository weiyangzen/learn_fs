# File Research: sources/os/bsd/netbsd-src/lib/libc/rpc/svc_raw.c

Read completely: 259 lines.

Implements the in-process “raw” RPC server transport used for testing/timing without kernel networking. A singleton `svc_raw_private` holds a shared raw buffer, embedded `SVCXPRT`, XDR memory stream, and verifier body. The buffer is shared with raw client code via global `__rpc_rawcombuf`.

`svc_raw_create()` initializes the singleton, sets `xp_fd = -1`, installs raw transport ops, creates an XDR decode stream over the shared buffer, and registers the transport. Receive/reply/getargs/freeargs operate on the shared memory XDR stream; destroy is a no-op.

All singleton access is serialized by `svcraw_lock`. This transport is intentionally process-local and not a real network service.
