# sources/user-network-fs/samba/source4/ntvfs/common/opendb_tdb.c

## Purpose

`opendb_tdb.c` implements the TDB-backed source4 NTVFS open-file database. It coordinates share-mode enforcement, delete-on-close, pending-open retry notifications, write-time state, and oplock/lease behavior across server instances.

## Important APIs, Types, and Functions

Backend registration is `odb_tdb_init_ops()`. Internal types are `struct odb_context` and `struct odb_lock`. Important functions include `odb_tdb_init()`, `odb_tdb_lock()`, `odb_tdb_get_key()`, `odb_pull_record()`, `odb_push_record()`, `share_conflict()`, `odb_tdb_open_can_internal()`, `odb_tdb_can_open()`, `odb_tdb_open_file()`, `odb_tdb_open_file_pending()`, `odb_tdb_close_file()`, `odb_tdb_remove_pending()`, `odb_tdb_update_oplock()`, `odb_tdb_break_oplocks()`, `odb_tdb_rename()`, `odb_tdb_get_path()`, `odb_tdb_set_delete_on_close()`, `odb_tdb_set_write_time()`, and `odb_tdb_get_file_infos()`.

## Control Flow

Init opens the `openfiles` cluster temp DB, reads share oplock settings, and creates a sys-lease context. Lock fetches and locks a file-key record, then decodes an NDR `opendb_file` or initializes an empty record. `odb_tdb_can_open()` checks batch oplocks, delete pending state, delete-on-close conflict, share conflicts, exclusive oplocks, and records a pending `opendb_entry` for the subsequent open. `odb_tdb_open_file()` finalizes that entry, grants an oplock level based on existing opens and attribute-only access, sets up a sys lease if possible, appends the entry, and stores the NDR record. Close removes the matching entry, propagates delete-on-close, removes leases, sends pending-open retry messages, and deletes or updates the DB record.

## State and Persistence Behavior

Runtime persistent state is NDR-encoded `struct opendb_file` in `openfiles.tdb`, keyed by caller-provided file identity blobs. Records contain path, entries, pending opens, delete-on-close, open write time, and changed write time. Oplock breaks use imessaging to the server that owns the open; sys leases mirror oplock state to the local OS when available.

## Dependencies and Integration Points

It depends on dbwrap, cluster DB helpers, generated `ndr_opendb`, NTVFS contexts, imessaging, sys-lease backends, share options, access masks, and oplock constants. Disk backends call it through `opendb.c` before and after filesystem opens and closes.

## Risks and Edge Cases

Callers must call `odb_can_open()` and `odb_open_file()` with the same lock handle; otherwise `odb_open_file()` returns internal error. Batch and exclusive oplock handling intentionally returns `NT_STATUS_OPLOCK_NOT_GRANTED` to make callers retry after breaks. Attribute-only access bypasses some oplock breaks and suppresses oplock grants. Pending-open messages are sent and cleared on close or oplock update. Pointer-valued file handles and fd pointers are stored in NDR records with server IDs, so they are meaningful only to the owning process.

## Test Signals

Tests should cover share conflicts for read/write/delete masks and streams, delete pending, delete-on-close with existing opens, can-open/open sequencing, oplock grant downgrade rules, batch/exclusive/level2 break paths, pending-open retry messages, lease setup/update/remove, rename/path lookup, write-time force semantics, and final delete path when last open closes with delete-on-close.
