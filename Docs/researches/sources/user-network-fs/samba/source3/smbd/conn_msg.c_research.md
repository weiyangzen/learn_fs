# sources/user-network-fs/samba/source3/smbd/conn_msg.c

## Purpose
`conn_msg.c` handles smbcontrol messaging requests that force tree disconnects by share name, either unconditionally or only when access after a service reload is no longer valid.

## Important APIs, types, and functions
- `msg_force_tdis()` validates a NUL-terminated share name and calls `conn_force_tdis()` with `force_tdis_check()`.
- `force_tdis_check()` matches a literal share name or `*` for all shares.
- `msg_force_tdis_denied()` reloads services as root and then forces disconnects selected by `force_tdis_denied_check()`.
- `force_tdis_denied_check()` re-runs `check_user_share_access()` and closes only if access fails, share access bits changed, or read-only state changed.

## Control flow
Both message handlers treat message data as a C string and reject empty or non-NUL-terminated payloads. The unconditional path just compares the requested name against each connection's service name. The denied path first reloads service definitions, then for matching connections recomputes access and closes only sessions whose effective access no longer matches the connection's stored `share_access`/`read_only` fields.

## State and persistence behavior
This file does not persist state directly. It can trigger async TCON disconnects, connection closing, and service reload through `conn_force_tdis()`. The message payload is transient.

## Dependencies and integration points
It depends on smbd messaging, loadparm service names, user share access checks, and `conn_idle.c`'s forced disconnect implementation. It is typically driven by administrative smbcontrol operations and share/service reload notifications.

## Risks and edge cases
- Message payload validation is critical because the share name is read directly from `DATA_BLOB`.
- `*` closes all shares and logs a warning for each matching connection.
- Access-revalidation close behavior depends on current service reload state and session security tokens.
- Failure in `check_user_share_access()` intentionally closes the share.

## Test signals
Tests should send valid and invalid message payloads, force-disconnect a named share and all shares, change share ACL/read-only configuration and verify only denied or changed connections close, and verify unaffected connections remain active.
