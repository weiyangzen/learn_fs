# sources/user-network-fs/samba/source3/lib/cleanupdb.c

Purpose: tracks smbd child cleanup obligations in a shared TDB so cleanupd can discover children that exited cleanly or uncleanly.

Important APIs/types/functions: private `struct cleanup_key`, `struct cleanup_rec`, singleton `cleanup_db()`, public `cleanupdb_store_child()`, `cleanupdb_delete_child()`, and `cleanupdb_traverse_read()`.

Control flow: `cleanup_db()` lazily opens `lock_path("smbd_cleanupd.tdb")` with incompatible hash, clear-if-first, and mutex locking. Store/delete wrap pid keys in fixed-size TDB records. Traversal validates key/value sizes, copies them into local structs, and invokes the caller callback.

State and persistence: persistent TDB at Samba lock path; static `struct tdb_wrap *db` caches the handle for process lifetime. `TDB_CLEAR_IF_FIRST` resets the DB when the first process opens it after all handles are gone.

Dependencies/integration: tdb_wrap, TDB mutex locking, Samba lock path utility, talloc stack, DEBUG.

Risks/test signals: fixed binary pid/bool layouts are host ABI dependent and intended only for local runtime state. Traversal aborts on malformed records. Tests should store/delete pids, traverse multiple records, reject malformed TDB entries, verify lock path/open flags, and simulate missing DB/open failure.
