# Research: sources/user-network-fs/samba/source3/lib/netapi/netapi_private.h

Purpose: private implementation header for Samba's NetAPI support. It defines the concrete `libnetapi_ctx`, internal private state, localhost-redirection macro for local wrappers, and helper prototypes used by SAMR, SRVSVC, NETLOGON, shutdown, and group/user code.

Important APIs/types: `struct libnetapi_private_ctx` caches SAMR domain metadata, `rpc_pipe_client`, connect/domain/builtin access masks, and policy handles, plus IPC connections and a messaging context. `struct libnetapi_ctx` stores debug/log/error strings, policy handle cache toggle, credentials, private data, and loadparm context. Helper prototypes include error/log setters, RPC pipe/binding acquisition, SAMR domain open/close/free routines, and `add_GROUP_USERS_INFO_X_buffer`.

Control flow: `LIBNETAPI_REDIRECT_TO_LOCALHOST(ctx, r, fn)` logs the redirection, defaults a missing `r->in.server_name` to `"localhost"`, and tail-calls the remote `_r` version. SAMR helpers centralize connection/domain handle acquisition and cache management so higher-level user/group/localgroup operations do not duplicate RPC setup.

State and persistence: state is process-local in `libnetapi_ctx` and its `private_data`. Cached policy handles persist for the lifetime of the context unless masks are insufficient or explicit close/free functions run. Persistent effects occur only through downstream RPC calls, not from this header itself.

Dependencies/integration: includes `netapi_net.h` and Samba credential declarations. It references generated NDR interface tables, DCE/RPC binding handles, RPC pipe clients, policy handles, domain SIDs, client IPC connections, messaging contexts, and loadparm state. Implementation files include it to access the concrete context hidden from public `netapi.h`.

Risks: policy-handle caching requires access-mask checks to be exact; using a cached handle with insufficient rights would break later operations, while failing to close stale handles leaks server-side resources. The redirect macro mutates request input by assigning `server_name`, which can surprise callers inspecting request structs after local calls. `talloc_get_type_abort` in implementations means corrupted or missing private data aborts rather than returning a NetAPI error.

Test signals: targeted tests should cover handle cache reuse, cache invalidation when requested masks grow, cleanup via `libnetapi_samr_free`, localhost redirection when `server_name` is NULL, and error-string propagation from helper failures.
