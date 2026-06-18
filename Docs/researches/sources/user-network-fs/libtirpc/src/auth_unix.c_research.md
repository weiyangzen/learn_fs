<!-- BEGIN_FILE_RESEARCH: sources/user-network-fs/libtirpc/src/auth_unix.c -->
# sources/user-network-fs/libtirpc/src/auth_unix.c

Purpose: Implements AUTH_UNIX/AUTH_SYS style RPC client credentials.

Important APIs, types, and functions: Exports `authunix_create` and `authunix_create_default`; implements auth ops, shorthand credential validation, refresh, destroy, and `marshal_new_auth` cache generation.

Control flow: Creation serializes machine name, uid, gid, groups, and current time into an opaque AUTH_UNIX credential, stores original credential, then pre-marshals credential/verifier. Default creation queries hostname/euid/egid/groups with retry for group-list growth. Validate accepts AUTH_SHORT verifiers and switches to shorthand credentials. Refresh falls back from shorthand to original credentials and updates timestamp.

State and persistence behavior: Per-AUTH private `audata` stores original credential, shorthand credential, fault count, and pre-marshaled bytes. Destroy frees credential buffers and AUTH.

Dependencies and integration points: Depends on POSIX identity/group calls, XDR authunix parms, `_null_auth`, and auth ops locks. Core source in libtirpc build.

Risks: AUTH_UNIX is unauthenticated and easily spoofed. Group list truncates to `NGRPS`. Cached marshaling must be refreshed whenever credentials change. Warning text in `marshal_new_auth` names `auth_none.c`, likely copy/paste.

Test signals: Indirectly exercised by normal RPC clients; no direct unit test in this subset.
<!-- END_FILE_RESEARCH: sources/user-network-fs/libtirpc/src/auth_unix.c -->
