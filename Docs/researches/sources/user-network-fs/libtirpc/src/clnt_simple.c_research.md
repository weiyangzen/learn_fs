## sources/user-network-fs/libtirpc/src/clnt_simple.c

Purpose: Provides `rpc_call`, the simplified one-shot RPC API that internally caches a client handle for repeated calls to the same host/program/version/nettype.

Important APIs and control flow: `rpc_call` creates a thread-specific `rpc_call_private` key on first use, then reuses the cached `CLIENT` only if pid, program, version, host, and nettype still match. On cache miss it destroys the old client, calls `clnt_create`, sets a 5-second retry timeout, marks the fd close-on-exec, stores identity fields when they fit fixed buffers, and calls `CLNT_CALL` with a 25-second total timeout. Failures invalidate the cache.

State and persistence: Cache is thread-specific and pid-aware to avoid reuse after fork. The destructor destroys the cached client at key cleanup.

Dependencies and integration: Wraps `clnt_create`, `CLNT_CONTROL`, and `CLNT_CALL`. Defaults empty nettype to `netpath`.

Risks and test signals: Fixed host/nettype buffers only cache short values. Tests should cover cache hit/miss, fork pid change, failure invalidation, close-on-exec flag, default netpath, and thread-local isolation.
