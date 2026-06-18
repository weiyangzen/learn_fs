# sources/user-network-fs/samba/source3/rpc_server/rpc_config.h

Purpose: declares the global DCE/RPC context accessor and free function for source3 RPC server code.

Important APIs: forward declares `struct dcesrv_context`, exports `global_dcesrv_context(void)`, and `global_dcesrv_context_free(void)`.

Control flow and integration: consumers include this header to obtain the lazily initialized server context without depending on the implementation details in `rpc_config.c`.

State and persistence: the state is the implementation singleton; the header exposes no mutable globals.

Dependencies: minimal by design, avoiding heavy DCE/RPC includes in consumers that only need an opaque pointer.

Risks: callers must not assume ownership of the returned context. Freeing the global context while active RPC users still exist would invalidate shared state.

Test signals: build coverage and integration tests around RPC startup/shutdown are the relevant checks.
