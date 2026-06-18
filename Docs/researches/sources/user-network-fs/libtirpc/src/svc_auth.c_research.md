<!-- BEGIN_FILE_RESEARCH: sources/user-network-fs/libtirpc/src/svc_auth.c -->
# sources/user-network-fs/libtirpc/src/svc_auth.c

Purpose: server-side authentication dispatcher. It maps incoming credential flavors to built-in or registered authentication handlers.

Important APIs and functions: `_gss_authenticate()` is the main dispatcher and supports `AUTH_NONE`, `AUTH_SYS`, `AUTH_SHORT`, optional `AUTH_DES`, optional `RPCSEC_GSS`, and custom flavors. `_authenticate()` is a compatibility wrapper. `svc_auth_reg()` registers custom handlers in a linked list.

Control flow: authentication initialization copies raw credentials to the request, resets the transport `SVCAUTH` ops to `svc_auth_none`, clears private auth state, resets the reply verifier to `_null_auth`, and dispatches by credential flavor. Unknown flavors are looked up under `authsvc_lock`. Custom registration rejects already built-in flavors, prevents duplicate custom entries, and prepends new handler nodes.

State and persistence: static linked list `Auths` persists for process lifetime and has no unregister path. Transport auth state is reset per request before flavor-specific handling.

Dependencies and integration points: called from `svc_getreq_common()` before service dispatch. Integrates with `svc_auth_none.c`, `svc_auth_unix.c`, `svc_auth_des.c`, and `svc_auth_gss.c`.

Risks: registered custom handlers are never freed. `AUTH_NULL` and `AUTH_NONE` naming differences are handled through constants, but custom flavor validation must match platform definitions. Built-in GSS can set `no_dispatch`, which callers must honor.

Test signals: all built-in flavor branches, GSS handshake no-dispatch behavior, custom handler registration and duplicate detection, unknown flavor rejection, and transport verifier reset between mixed-auth requests.
<!-- END_FILE_RESEARCH: sources/user-network-fs/libtirpc/src/svc_auth.c -->
