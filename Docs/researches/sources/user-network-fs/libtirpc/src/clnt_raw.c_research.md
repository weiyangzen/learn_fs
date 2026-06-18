## sources/user-network-fs/libtirpc/src/clnt_raw.c

Purpose: Implements an in-process memory-backed RPC client used with raw service transports for tests and microbenchmarks without kernel networking.

Important APIs and control flow: `clnt_raw_create` lazily allocates one global `clntraw_private`, initializes `__rpc_rawcombuf`, pre-marshals the call header, and returns a singleton `CLIENT` using `authnone`. `clnt_raw_call` writes request data into the shared XDR memory stream, invokes `svc_getreq_common(FD_SETSIZE)` directly to let the in-process server handle it, then decodes the reply from the same buffer. It handles partial decode cleanup and auth refresh retry. `clnt_raw_freeres` switches the shared XDR stream to `XDR_FREE`.

State and persistence: Singleton private state and raw buffer persist for the process lifetime. `clnt_raw_destroy` is intentionally a no-op.

Dependencies and integration: Integrates with `svc_raw_create`/raw service machinery through `__rpc_rawcombuf` and `svc_getreq_common`.

Risks and test signals: The singleton design means no independent raw clients. Tests should cover raw client/server round trips, auth refresh, decode failure cleanup, XDR free paths, and lock behavior under concurrent raw calls.
