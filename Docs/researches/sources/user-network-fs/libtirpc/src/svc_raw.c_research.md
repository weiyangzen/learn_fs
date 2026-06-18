<!-- BEGIN_FILE_RESEARCH: sources/user-network-fs/libtirpc/src/svc_raw.c -->
# sources/user-network-fs/libtirpc/src/svc_raw.c

Purpose: in-process raw server transport for testing and timing RPC without kernel networking.

Important APIs and functions: `svc_raw_create()` creates/reuses the singleton raw `SVCXPRT`. Transport ops are `svc_raw_recv()`, `svc_raw_reply()`, `svc_raw_getargs()`, `svc_raw_freeargs()`, `svc_raw_destroy()`, `svc_raw_stat()`, and `svc_raw_control()`. Global `__rpc_rawcombuf` is the shared client/server buffer.

Control flow: first creation allocates singleton private state, extension storage, and the shared buffer if needed; later calls reuse it. The server fd is set to `FD_SETSIZE`, ops are installed, verifier storage is assigned, an XDR memory stream is created over the shared buffer, and the transport is registered. Receive decodes a call message from offset zero; reply encodes a reply message back to offset zero; getargs/freeargs call the supplied XDR procedure on the same memory stream.

State and persistence: singleton `svc_raw_private` and `__rpc_rawcombuf` persist for process lifetime. `svcraw_lock` protects singleton access, but the raw transport remains a shared non-reentrant testing mechanism.

Dependencies and integration points: pairs with raw client transport code through the shared buffer and uses the normal `svc.c` transport registry/dispatch.

Risks: not a real network transport and not suitable for concurrent independent sessions. `svc_raw_destroy()` does nothing, so registration/state can persist. The fake fd value can interact awkwardly with descriptor-table assumptions.

Test signals: raw client/server NULLPROC and argument round trips, repeated `svc_raw_create()` reuse, concurrent call behavior documentation, freeargs path, and cleanup expectations around no-op destroy.
<!-- END_FILE_RESEARCH: sources/user-network-fs/libtirpc/src/svc_raw.c -->
