# File Research: sources/os/bsd/netbsd-src/lib/libc/rpc/clnt_raw.c

Read completely: 314 lines.

This file implements in-process memory-backed RPC clients for testing/timing: `clnt_raw_create` and raw client ops.

Key behavior: lazily allocates a global raw client/private object and shared `__rpc_rawcombuf`, pre-serializes a call header, and uses one XDR memory stream over the shared buffer. Calls encode request bytes, invoke `svc_getreq_common(-1)` directly to simulate server processing in the same process, then decode the reply, validate auth, refresh credentials if needed, and free partial reply allocations on decode failure.

Important interactions: pairs with raw service transport and shared RPC raw buffer; default auth is AUTH_NONE.

Security/reliability notes: global shared buffer and client object are protected by `clntraw_lock` around setup but the call path uses shared state, so this is mainly for local testing rather than independent concurrent conversations.
