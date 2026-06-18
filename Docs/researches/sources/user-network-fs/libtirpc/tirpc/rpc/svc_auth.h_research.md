# sources/user-network-fs/libtirpc/tirpc/rpc/svc_auth.h

Purpose: `svc_auth.h` defines the server-side authentication vtable and authentication dispatch registration APIs.

Important APIs, types, and functions: It defines `SVCAUTH`, `struct svc_auth_ops`, macros `SVCAUTH_WRAP`, `SVCAUTH_UNWRAP`, `SVCAUTH_DESTROY`, and functions `_gss_authenticate`, `_authenticate`, and `svc_auth_reg`.

Control flow: Server transports use `_authenticate` to validate a decoded RPC message and populate request credentials. Authenticated service replies use `SVCAUTH_WRAP`/`UNWRAP` through the per-transport auth object. New auth flavors can be registered by flavor number through `svc_auth_reg`.

State and persistence behavior: `SVCAUTH` instances carry a vtable and private data, usually embedded in `SVCXPRT_EXT`. Flavor registries and private auth contexts are implementation-owned.

Dependencies and integration points: It depends on `struct svc_req`, `struct rpc_msg`, `XDR`, and auth status definitions from other RPC headers. `svc_vc.c` calls `SVCAUTH_UNWRAP` and `SVCAUTH_WRAP`.

Risks: Vtable macros have no null checks. Auth flavor registration must be synchronized in multithreaded code. GSS authentication returns an extra no-dispatch flag, so callers must handle handshake/control messages correctly.

Test signals: Tests should cover AUTH_NONE/UNIX/GSS authentication, custom flavor registration, wrap/unwrap error propagation, destroy cleanup, and rejected auth status replies.
