# sources/user-network-fs/samba/source3/smbd/smbXsrv_session.c

## Purpose
Implements Samba smbd's SMB1/SMB2 session lifecycle. It creates local session objects, persists cluster-visible global session records, handles multi-channel attachment/removal, coordinates SMB2 previous-session closure, shuts sessions down without racing outstanding requests, and exposes lookup/traversal helpers used by request validation and status enumeration.

## Important APIs, Types, and Functions
- `struct smbXsrv_session_table` owns a local in-memory `dbwrap_rbt` table of `local_id -> struct smbXsrv_session *` plus a shared global `smbXsrv_session_global.tdb`.
- `smbXsrv_session_global_init()` opens the volatile watched global TDB with mode `0600` because records contain session keys.
- `smbXsrv_session_create()`, `smbXsrv_session_add_channel()`, `smbXsrv_session_update()`, `smbXsrv_session_remove_channel()`, and `smbXsrv_session_logoff()` form the main lifecycle.
- `smb1srv_session_*` and `smb2srv_session_*` wrappers provide protocol-specific ID ranges and lookup semantics.
- `smb2srv_session_shutdown_send/recv()` implements async cancellation/waiting for in-flight requests and lease-break waits.
- `smb2srv_session_close_previous_send/recv()` uses watched dbwrap records plus messaging to close a previous authenticated SMB2 session for the same user SID.
- `smbXsrv_session_global_traverse()` and `smbXsrv_session_local_traverse()` expose enumeration hooks.

## Control Flow
Global init creates a watched dbwrap wrapper over `smbXsrv_session_global.tdb`; per-client table init creates a local rbt db and starts a persistent `messaging_read_send()` loop for `MSG_SMBXSRV_SESSION_CLOSE`. Creating a session allocates a local object, reserves a random global 32-bit ID, selects SMB2 wire IDs directly from the global ID or SMB1 IDs from the bounded local range, creates the SMB2 tcon table when needed, adds the initial channel, stores a local pointer record, then NDR-serializes the global record. Lookups parse local pointer records, reject deleted/expired sessions, and optionally verify the incoming connection is still a registered channel.

Shutdown marks the session `NT_STATUS_USER_SESSION_DELETED`, cancels other pending SMB2 subrequests, queues waiters until those requests drain, and waits for delete-on-close handle lease breaks. Logoff closes files by user ID, disconnects SMB2 tcons, invalidates the vuid, deletes global and local records, and decrements the local count. Multi-channel removal deletes pending auth/channel entries; if the last channel disappears, it starts async session shutdown and keeps the transport shutdown queue blocked until the session object is freed.

## State and Persistence
Local session state is process-local and stores raw pointers in the rbt db, so it is valid only in the owning smbd process. Global state is volatile TDB under the lock path, NDR encoded as `smbXsrv_session_globalB`, carries a sequence number, server IDs, channel metadata, auth session info, and secret key blobs. The verifier treats empty or stale records as free and deletes records whose primary channel server ID no longer exists. Secret blobs are marked with `talloc_keep_secret()`.

## Dependencies and Integration Points
Depends on dbwrap/rbt/watched TDB, messaging, serverid liveness, tevent, NDR generated `smbXsrv` types, gensec expiration constants, SMB2 signing/cipher constructors, share-mode/lease-break helpers, file close helpers, and tcon lifecycle from `smbXsrv_tcon.c`. It is used by SMB request validation, UID switching through `smbXsrv_session_info_lookup()`, SRVSVC-style global traversal, and SMB2 session setup/logoff paths.

## Risks
The local table stores raw pointers, so db corruption or misuse outside object lifetime is fatal. Session records include secrets and must remain `0600` and volatile. Correctness depends on dbwrap record locks and watched-record fairness in previous-session closure. Async shutdown must avoid cancelling the current request while guaranteeing all other requests and lease breaks drain. The code has many status-specific branches; treating `MORE_PROCESSING_REQUIRED`, expired, and deleted sessions interchangeably would break authentication or request validation.

## Test Signals
Exercise SMB1 and SMB2 login/logoff, invalid/zero/high-bit session IDs, session expiration, multi-channel disconnects, previous-session reconnect for the same SID, server crash cleanup of stale global records, and request cancellation during logoff. Tests should also inspect that global TDB records are removed on logoff and that uid switching can retrieve `auth_session_info` only after authentication completes.
