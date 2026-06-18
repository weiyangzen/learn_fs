# sources/user-network-fs/samba/source3/smbd/uid.c

## Purpose
Manages effective Unix/NT security context switching for smbd request handling. It validates share access for a session, caches per-vuid connection authorization state, applies force group/admin user semantics, switches to users or root, and exposes current effective token accessors.

## Important APIs, Types, and Functions
`change_to_guest()`, `check_user_share_access()`, `change_to_user_and_service()`, `change_to_user_and_service_by_fsp()`, `smbd_change_to_root_user()`, `smbd_become_authenticated_pipe_user()`, `smbd_unbecome_authenticated_pipe_user()`, `smbd_become_root()`, `smbd_unbecome_root()`, `become_user_without_service*()`, `unbecome_user_without_service()`, and `get_current_uid/gid/utok/nttok()` form the exported behavior. Internally, `check_user_ok()` populates the vuid cache and `change_to_user_impersonate()` applies the selected session token.

## Control Flow
Request paths lookup `auth_session_info` via `smbXsrv_session_info_lookup()`, call `change_to_user_impersonate()`, then optionally `chdir_current_service()`. `check_user_ok()` first reuses a matching vuid cache entry, otherwise validates `valid users`/share ACL/read-only state, calculates share access, handles admin users by mapping to initial uid, builds veto/hide lists including token-qualified parametric entries, and stores the result in a ring cache. Impersonation applies force group rules, updates the Unix token/security token group SID when forced, calls `set_sec_ctx()`, and updates global `current_user`.

Root and temporary user transitions push both the security context stack and a parallel connection context stack; pop restores current user metadata. Pipe impersonation uses only the security context stack and intentionally does not modify `current_user`.

## State and Persistence
Runtime state includes global `current_user`, `conn->session_info`, `conn->vuid_cache`, veto/hide lists, connection read-only/share access flags, and the connection context stack. No on-disk persistence is performed. Decisions are derived from smb.conf, passdb/session tokens, and share security descriptors.

## Dependencies and Integration Points
Depends on passdb lookups, auth/session info, security tokens and privileges, Samba loadparm substitution/parametrics, share access helpers, `smbXsrv_session_info_lookup()`, current security context stack helpers, and service chdir. It is central to VFS calls, file operations, named pipe operations, and SMB request execution.

## Risks
Incorrect stack push/pop pairing can leave smbd running as root or the wrong user. Vuid cache ownership is subtle because `conn->session_info` may point into cache entries; `free_conn_state_if_unused()` prevents double/free-live state mistakes. Force group changes mutate token fields and must stay consistent with SID updates. `UID_FIELD_INVALID` is deliberately allowed for internal no-service impersonation, but using it on wire-authenticated paths would weaken cache semantics.

## Test Signals
Test valid/invalid vuid switching, share ACL denial, read-only fallback from security descriptor, admin users, force group with and without `+`, dynamic force-group config changes on existing connections, veto/hide parametric entries matching token names, nested become/unbecome root/user calls, pipe impersonation, and current token accessors inside root override blocks.
