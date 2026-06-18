# sources/user-network-fs/samba/source3/rpc_server/rpc_config.c

Purpose: provides lazy global initialization and teardown for the source3 DCE/RPC server context.

Important APIs and functions: `global_dcesrv_context()` initializes a singleton `struct dcesrv_context` using `global_event_context()`, an S3 loadparm context from `loadparm_init_s3()`, and `srv_callbacks`. `global_dcesrv_context_free()` frees the singleton. Callback wiring provides successful authorization logging, GENSEC preparation, root/unroot hooks, and association-group lookup.

Control flow: the first caller gets initialization; later callers reuse `global_dcesrv_ctx`. The loadparm context is stolen under the DCE/RPC context to align lifetimes. Fatal initialization failures call `smb_panic()` because the RPC server cannot run without this context.

State and persistence: `global_dcesrv_ctx` is static process state. It is intentionally allocated from a NULL context rather than the autofree context to avoid forked-child exit side effects.

Dependencies: RPC server helpers, DCE/RPC core, loadparm S3 helpers, global event context, and Samba privilege transition callbacks.

Risks: singleton lifecycle must be coordinated across forked processes and shutdown. Any callback behavior affects all RPC interfaces using the global context. Panics are appropriate for startup failure but make memory/config failures fatal.

Test signals: initialization tests should verify singleton reuse, callback availability, and clean `global_dcesrv_context_free()` behavior. Integration tests should ensure forked RPC workers do not inherit unsafe autofree ownership.
