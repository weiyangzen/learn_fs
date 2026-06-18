# sources/user-network-fs/samba/source3/smbd/password.c

## Purpose
`password.c` contains small `smbd` session and homes-share helpers. It invalidates authenticated virtual user IDs and dynamically registers `[homes]` shares for users whose Unix account has a valid home directory.

## Important APIs, Types, And Functions
`invalidate_vuid(struct smbd_server_connection *sconn, uint64_t vuid)` looks up a live `smbXsrv_session` with `get_valid_smbXsrv_session()`. If found, it calls `session_yield()`, decrements `sconn->num_users`, and clears connection/session vuid caches with `conn_clear_vuid_caches()`.

`register_homes_share(const char *username)` checks whether a static or previously created service already exists with `lp_servicenumber()`. If so, it returns that service number. Otherwise it resolves the Unix account with `Get_Pwnam_alloc()`, rejects missing/empty home directories and `/`, and calls `add_home_service(username, username, pwd->pw_dir)`.

## Control Flow
Session invalidation is intentionally short. Invalid or already-gone vuids return without side effects. Valid sessions are yielded first, then the server connection user count is decremented under an assertion that it was positive, then all cached references to the vuid are cleared from connection state.

Homes registration first prefers existing loadparm services, which avoids recreating a dynamic share. If no service exists, it queries passwd data on the current talloc stack, validates the directory field, creates the home service, frees the passwd record, and returns the resulting service index or `-1`.

## State And Persistence
`invalidate_vuid()` mutates in-memory server state: the `smbXsrv_session`, `sconn->num_users`, and vuid caches on connections. Durable session database effects are delegated to `session_yield()`.

`register_homes_share()` mutates Samba service configuration through `add_home_service()`, creating an in-process dynamic service for the username. It reads but does not modify system passwd data. Allocations use `talloc_tos()` and are freed before return.

## Dependencies And Integration Points
The file depends on `smbXsrv_session` lookup/yielding, connection cache management, loadparm service lookup and substitution, passwd lookup, and service creation. Call sites include SMB1 and SMB2 session setup paths that register homes for authenticated Unix users, `srvsvc` service lookup for homes, and `smbXsrv_session.c` invalidation on session shutdown.

## Risks And Edge Cases
The main session risk is counter/cache consistency: `sconn->num_users` must only be decremented when a valid session was found, and all connection caches must be cleared after yielding. For homes, the safety checks prevent creating a share rooted at `/` or at an empty/missing path. Remaining risks are stale passwd/home data, username-to-service naming conflicts, and dynamic homes behavior differing across SMB1, SMB2, and RPC service enumeration paths.

## Test Signals
Relevant signals include SMB1/SMB2 session setup and logoff tests, dynamic `[homes]` blackbox coverage (`samba3.blackbox.homes` in `source3/selftest/tests.py`), and session teardown paths that exercise `invalidate_vuid()`. Focused tests should verify that repeated homes registration reuses the service, invalid home directories return `-1`, root home `/` is rejected, and vuid invalidation clears per-connection caches without underflowing `num_users`.
