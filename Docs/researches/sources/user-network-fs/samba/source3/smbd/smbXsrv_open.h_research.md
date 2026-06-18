# sources/user-network-fs/samba/source3/smbd/smbXsrv_open.h

## Purpose
This header declares the smbd SMBX open-handle management interface implemented by `smbXsrv_open.c`. It exposes global initialization, create/update/close, SMB1 and SMB2 lookup tables, SMB2 create replay cache lookup/purge, durable open recreation, global traversal, and cleanup APIs.

## Important APIs, Types, And Functions
The header forward-declares `smbXsrv_connection`, `auth_session_info`, `smbXsrv_open`, `smbXsrv_open_global0`, `smbXsrv_client`, `smbXsrv_session`, `smbXsrv_tcon`, `smb2_lease_key`, and `db_record`, keeping consumers decoupled from the concrete structures.

Public lifecycle calls are `smbXsrv_open_global_init()`, `smbXsrv_open_create()`, `smbXsrv_open_update()`, and `smbXsrv_open_close()`. Protocol-specific table APIs are `smb1srv_open_table_init()`, `smb1srv_open_lookup()`, `smb2srv_open_table_init()`, and `smb2srv_open_lookup()`.

Replay and durable APIs are `smbXsrv_open_purge_replay_cache()`, `smb2srv_open_lookup_replay_cache()`, `smb2srv_open_recreate()`, `smbXsrv_open_cleanup()`, and `smbXsrv_replay_cleanup()`. `smbXsrv_open_global_traverse()` exposes a callback-based iterator that can return either a parsed global open record or a replay-cache value key.

## Control Flow
Callers initialize global/table state during connection setup, create an open after successful file create, update it when durable/replay/create metadata changes, look it up for request file ids, and close it during file teardown. SMB2 create handling also calls the replay-cache lookup before normal create processing and calls recreate when durable reconnect is required.

The traverse API inverts control: callers pass a callback taking a locked `db_record`, optional `smbXsrv_open_global0`, optional replay-cache key value, and private data. Cleanup APIs are called by housekeeping or reconnect failure paths to delete stale persistent/replay state.

## State And Persistence Behavior
The header itself has no state, but its functions govern the persistent `smbXsrv_open_global.tdb` records and in-memory per-client open tables. The exposed parameters make the identity model explicit: SMB2 file ids are `persistent_id` plus `volatile_id`; replay identity is client GUID plus create GUID; durable recreation may also validate create GUID and lease key.

## Dependencies And Integration Points
Includes are minimal: `replace.h`, NTSTATUS, NTTIME, `DATA_BLOB`, and generated misc GUID definitions. This lets SMB2 create/read/write/setinfo/close code, cleanup code, and debugging/traversal code share the open-management contract without including the implementation's dbwrap, idtree, or NDR details.

## Risks And Edge Cases
Because this is a cross-module contract, signature changes can affect many SMB1/SMB2 handlers. The callback shape for traversal is especially easy to misuse because either `global` or `rc_open_global_key` may be present depending on record type. Callers must also preserve the distinction between SMB2 persistent and volatile ids and must not treat replay-cache statuses as generic lookup errors.

## Test Signals
Header-level test signal comes from successful compilation of all smbd consumers plus runtime coverage of create/update/close, SMB1 lookup, SMB2 file-id lookup, replay-cache lookup/purge, durable reconnect, traversal, and cleanup paths.
