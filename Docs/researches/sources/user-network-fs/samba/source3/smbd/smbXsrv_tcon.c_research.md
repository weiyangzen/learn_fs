# sources/user-network-fs/samba/source3/smbd/smbXsrv_tcon.c

## Purpose
Implements tree-connection lifecycle for smbd. A tcon represents a client connection to a share; this file allocates IDs, stores global tcon records for server-wide enumeration, maps local IDs to live tcon pointers, updates records, and disconnects one or all tcons for SMB1 clients or SMB2 sessions.

## Important APIs, Types, and Functions
- `struct smbXsrv_tcon_table` mirrors the session table pattern with local rbt and global volatile TDB stores.
- `smbXsrv_tcon_global_init()` opens `smbXsrv_tcon_global.tdb`.
- `smbXsrv_tcon_create()`, `smbXsrv_tcon_update()`, and `smbXsrv_tcon_disconnect()` implement lifecycle.
- `smb1srv_tcon_table_init/create/lookup/disconnect_all()` operate on the client-level SMB1 table.
- `smb2srv_tcon_table_init/create/lookup/disconnect_all()` operate under an SMB2 session.
- `smbXsrv_tcon_global_traverse()` enumerates global records as `smbXsrv_tcon_global0`.

## Control Flow
Table initialization validates ID bounds, opens an rbt local table, and attaches the shared global TDB. Creation allocates a random global ID, stores share name, session global ID, encryption flags, server ID, creation time, and protocol-specific wire/local IDs, then stores a local pointer record and NDR-encoded global record. SMB1 uses 16-bit local tree IDs; SMB2 uses the low 32-bit global ID while keeping the maximum live tcon count aligned with SMB1.

Disconnect first closes the compatibility `connection_struct` with `close_cnum()` after changing to the service directory, marks the tcon deleted, deletes the global and local records, and decrements the count. Disconnect-all traverses local records, extracts each live pointer, selects the right vuid, and calls the single-disconnect path.

## State and Persistence
Local state is an in-memory pointer table scoped to a client or session. Global state is volatile TDB encoded as `smbXsrv_tcon_globalB`, storing IDs, share name, server ID, encryption flags, and sequence number. Verification removes stale records when the owning server ID no longer exists. The compatibility connection pointer links tcon lifetime to the older service/connection layer.

## Dependencies and Integration Points
Depends on dbwrap/rbt/open, generated NDR `smbXsrv` types, serverid liveness, messaging server IDs, service close/chdir helpers, and session lifecycle. SMB2 session logoff calls `smb2srv_tcon_disconnect_all()`, and SMB1 client teardown calls `smb1srv_tcon_disconnect_all()`.

## Risks
As with sessions, local records store raw pointers and require strict object lifetime. Disconnect must always call `close_cnum()` when `compat` exists, even after `chdir_current_service()` failure, otherwise the connection list can retain a soon-to-be-freed pointer. Global verification does not mark malformed records free in all branches, so corrupt TDB records may cause allocation pressure or traversal warnings. SMB1 tcons may have stale or wrong vuids, a behavior explicitly preserved for compatibility.

## Test Signals
Test SMB1/SMB2 tree connect and disconnect, tcon ID exhaustion, stale global records after process death, disconnect-all on session logoff, share close failure paths, and global traversal output for active shares. Include coverage for encrypted share flags and share-name persistence in global records.
