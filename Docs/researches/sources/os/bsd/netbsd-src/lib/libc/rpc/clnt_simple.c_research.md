# File Research: sources/os/bsd/netbsd-src/lib/libc/rpc/clnt_simple.c

Read completely: 218 lines.

This file implements `rpc_call`, a simplified cached frontend to client RPC.

Key behavior: keeps a cached `CLIENT` per thread when threaded, or one process-global cache otherwise. It reuses the client when pid, host, program, version, and nettype match; otherwise destroys and recreates it with `clnt_create`. It defaults empty nettype to `netpath`, sets a 5-second retry timeout, marks the fd close-on-exec when available, performs a 25-second total-timeout call, and invalidates the cache on failure.

Important interactions: convenience wrapper over generic client creation and `CLNT_CALL`; uses thread-specific cleanup to destroy cached clients.

Security/reliability notes: cache keys are bounded by fixed host/nettype arrays; overlong values disable caching rather than overflowing. Fork detection via stored pid prevents reusing a pre-fork client in a child.
