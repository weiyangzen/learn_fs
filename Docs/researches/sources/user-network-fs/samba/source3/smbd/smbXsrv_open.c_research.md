# sources/user-network-fs/samba/source3/smbd/smbXsrv_open.c

## Purpose
This file manages SMBX open-handle identity for SMB1 and SMB2. It allocates local volatile ids, stores global/persistent open records in `smbXsrv_open_global.tdb`, supports durable/disconnected opens, implements SMB2 create replay cache handling, recreates durable handles, traverses global open state, and cleans expired or stale open/replay records.

## Important APIs, Types, And Functions
`struct smbXsrv_open_table` contains the local id allocator and global DB context. The local side uses an `idr_context` bounded by protocol-specific id ranges; the global side uses a TDB database shared across smbd processes.

`smbXsrv_open_global_init()` opens `smbXsrv_open_global.tdb`. `smbXsrv_open_global_id_to_key()` converts 32-bit global ids to big-endian TDB keys so in-memory dbwrap ordering matches integer order. `smbXsrv_open_global_parse_record()`, `smbXsrv_open_global_verify_record()`, `smbXsrv_open_global_lookup()`, and `smbXsrv_open_global_store()` handle NDR serialization, version validation, stale-server detection, sequence numbers, and locked updates.

`smbXsrv_open_create()` allocates a local open object and local id, initializes `smbXsrv_open_global0`, records owner SID, session/tcon global ids, client GUID for SMB2.1+, random-allocates a global id, and stores the global record. `smbXsrv_open_update()` rewrites the global record and populates the replay cache if requested. `smbXsrv_open_close()` marks an open closed, stores a disconnected durable record or deletes a nondurable one, clears replay cache for nondurable opens, removes the local id, and frees the compat `files_struct`.

SMB1 and SMB2 table/lookup entry points are `smb1srv_open_table_init()`, `smb1srv_open_lookup()`, `smb2srv_open_table_init()`, and `smb2srv_open_lookup()`. SMB2 lookups validate high 32 bits, match volatile and persistent ids, refresh idle time, and clear the replay cache once the client proves it received the create response.

Replay-cache functions are `smbXsrv_open_replay_cache_key()`, `smbXsrv_open_set_replay_cache()`, `smbXsrv_open_purge_replay_cache()`, `smbXsrv_open_clear_replay_cache()`, and `smb2srv_open_lookup_replay_cache()`. Durable reconnect is implemented by `smb2srv_open_recreate()` and `smb2srv_open_recreate_fn()`. Cleanup and traversal use `smbXsrv_open_global_traverse()`, `smbXsrv_open_cleanup()`, and `smbXsrv_replay_cleanup()`.

## Control Flow
Open table initialization selects an id range and maximum open count, creates the local IDR allocator, initializes the global DB, and attaches the table to the client. SMB1 uses 1..65534. SMB2 allows a wider `int`-bounded local id space, but max opens is still capped by `real_max_open_files` and currently truncated to the SMB1-like limit.

Create flow allocates local first, initializes global metadata, then repeatedly tries random 32-bit global ids. Each candidate is locked and verified. Empty slots are stored. Live records cause retry. Records for dead smbd processes can be deleted and then retried, with a small delay before immediate id reuse.

Lookup flow is intentionally two-tiered. The local volatile id finds an in-process `smbXsrv_open`; the global/persistent id confirms it is the intended open. SMB1 treats the global check as a no-op by passing zero.

Replay-cache lookup has three major states. No record creates a reservation and returns `NT_STATUS_FWP_RESERVED`. A record with global id zero means the original create is still pending and returns `NT_STATUS_FILE_NOT_AVAILABLE`. A record with a valid global id looks up the original global open; if a matching local open exists and session matches, it returns that open, otherwise it returns `NT_STATUS_HANDLE_NO_LONGER_VALID` with the persistent id to trigger reconnect.

Durable recreate validates the persistent id width, allocates a fresh local open id, locks the global record, requires a disconnected durable record, optionally validates client GUID and create GUID, checks the current user's token contains the original owner SID, updates volatile id/server/session/tcon fields, stores the record, and returns the recreated local open.

Cleanup locks the global id, deletes corrupt, expired disconnected, or dead-server records, and then deletes the associated replay-cache key if a create GUID was present. Traversal distinguishes normal open records from fixed-size replay-cache records and reports either the parsed global open or the replay-cache global-key value to the callback.

## State And Persistence Behavior
The local `idr_context` maps volatile ids to in-process `smbXsrv_open` objects and tracks `num_opens`. The global TDB maps persistent/global ids to NDR-encoded `smbXsrv_open_global0` records. For SMB2 durable handles, close does not delete the global record; it sets a disconnected server id, disconnect time, clears session/tcon ids, and stores the durable state for later reconnect until timeout cleanup.

Replay cache records live in the same global DB but use a key composed from client GUID and create GUID, with a value containing the global open id key. A zero global id value is a pending reservation. Replay cache entries are removed when normal file-id lookup proves the client received the original response, when create failure purges a reservation, or during cleanup.

Open global records hold persistent id, volatile id, server id, open time, disconnect time, owner SID, session/tcon global ids, client GUID, create GUID, durable flags and timeout, and lock sequence array state. Store operations preserve and increment a record sequence number embedded in the NDR wrapper.

## Dependencies And Integration Points
The file integrates with generated `ndr_smbXsrv` structures, Samba dbwrap, random id generation, server-id liveness, messaging server ids, session/tcon/auth state, GUID/lease structures, durable-handle reconnect logic in create handling, file close/free logic, and replay cleanup callers.

It is the authoritative handle id layer used by SMB1 fnum lookup and SMB2 persistent/volatile file id lookup. Other smbd paths depend on it for resolving request file ids, durable handle reconnect, create replay idempotence, and global open cleanup after crashes or timeouts.

## Risks And Edge Cases
Persistent id allocation must avoid collisions and premature id reuse. Corrupt records, dead smbd records, and disconnected durable records all have different meanings. A bad status mapping can leak handles, break durable reconnect, or make clients retry indefinitely.

Replay-cache semantics are subtle. Returning the wrong status for pending, successful same-process replay, successful other-process replay, or stale record cases changes SMB2 create idempotence and durable reconnect behavior. Clearing replay cache too early can make a replay fail; clearing too late can accept duplicate creates.

Security risks include reconnecting a durable handle for a user whose token does not contain the original owner SID, accepting mismatched client/create GUIDs, or ignoring high 32 bits in SMB2 ids incorrectly. Cleanup risks include deleting live durable records or failing to remove expired replay records.

## Test Signals
Relevant signals are SMB2 create replay tests, durable-handle v1/v2 reconnect tests, persistent/volatile id validation, session mismatch replay returning duplicate-object behavior, crash/stale-record cleanup, durable timeout cleanup, multi-process reconnect, SMB1 fnum lookup, maximum-open exhaustion, replay reservation purge on failed create, and traversal consumers such as status/debug tooling.
