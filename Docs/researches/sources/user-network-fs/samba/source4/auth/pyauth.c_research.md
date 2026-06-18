<!-- BEGIN_FILE_RESEARCH: sources/user-network-fs/samba/source4/auth/pyauth.c -->
# sources/user-network-fs/samba/source4/auth/pyauth.c

Purpose: Python extension module `samba/auth.so` exposing session-info helpers and an `AuthContext` object for Samba authentication and authorization scripting/tests.

Important APIs: module functions include `system_session(lp_ctx=None)`, `admin_session(lp_ctx, sid)`, `user_session(ldb, lp_ctx=None, principal=None, dn=None, session_info_flags=0)`, `session_info_fill_unix(session_info, user_name, lp_ctx=None)`, `session_info_set_unix(session_info, user_name, uid, gid, lp_ctx=None)`, and `copy_session_info(session_info)`. `AuthContext.__new__(lp_ctx=None, ldb=None, methods=None)` creates an auth4 context with default or explicit methods. The module exports `AUTH_SESSION_INFO_*` constants.

Control flow: session functions validate Python NDR/pytalloc types, convert Python loadparm and LDB objects, allocate talloc frames, call native auth/session helpers, and convert results back via `py_return_ndr_struct()`. `py_auth_context_new()` creates loadparm, optional LDB, a Samba event context, default or explicit methods, then calls `auth_context_create()` or `auth_context_create_methods()`. It talloc-references loadparm and event context to keep them alive with the auth context.

State and persistence: Python objects wrap talloc-owned native `auth_session_info` or `auth4_context`. Some session objects are stolen to NULL before returning to Python. `AuthContext` retains references to `lp_ctx` and event context but exposes no methods in this file beyond construction.

Dependencies and integration: depends on Python C API, pytalloc, pyldb, pyparam, pycredentials, security helpers, auth/session APIs, Samba events, and pyrpc utilities. It is a key Python test fixture for auth/session construction.

Risks and test signals: type validation paths should raise Python exceptions without leaking frames. `system_session()` calls `system_session(lp_ctx)` then frees the temporary loadparm context, so tests should verify returned NDR object owns needed memory. AuthContext tests should cover explicit method lists, supplied LDB vs default samdb connection, invalid SID/DN/session types, Unix token fill/set failures, and exported constants.
<!-- END_FILE_RESEARCH: sources/user-network-fs/samba/source4/auth/pyauth.c -->
