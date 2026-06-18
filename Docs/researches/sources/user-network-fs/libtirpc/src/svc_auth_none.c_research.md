<!-- BEGIN_FILE_RESEARCH: sources/user-network-fs/libtirpc/src/svc_auth_none.c -->
# sources/user-network-fs/libtirpc/src/svc_auth_none.c

Purpose: no-auth server authenticator for AUTH_NONE/AUTH_NULL style requests.

Important APIs and functions: defines `svc_auth_none_ops`, global `svc_auth_none`, `_svcauth_none()`, `svcauth_none_wrap()`, and `svcauth_none_destroy()`.

Control flow: `_svcauth_none()` always returns `AUTH_OK`. Wrap and unwrap operations are the same function and simply call the provided XDR function on the supplied pointer without integrity or privacy transformation. Destroy is a no-op that returns true.

State and persistence: global `svc_auth_none` has ops and null private state. No per-request state is allocated.

Dependencies and integration points: `svc_auth.c` installs these ops as the default transport auth ops before every authentication attempt and dispatches to `_svcauth_none()` for `AUTH_NONE`.

Risks: no authentication, authorization, integrity, or privacy is provided. Callers must rely on higher-level access controls when accepting AUTH_NONE.

Test signals: AUTH_NONE request dispatch succeeds, wrap/unwrap invokes arbitrary XDR functions exactly once, destroy is harmless, and mixed requests reset transport auth ops back to no-auth before flavor-specific handling.
<!-- END_FILE_RESEARCH: sources/user-network-fs/libtirpc/src/svc_auth_none.c -->
