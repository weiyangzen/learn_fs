# sources/object-store/openstack-swift/swift/common/db.py

## Purpose
`db.py` provides Swift's shared SQLite broker infrastructure for account and container databases. It supplies eventlet-friendly SQLite connections, database creation and connection setup, pending-file batching, metadata management, replication sync points, tombstone reclamation, deletion state helpers, quarantine behavior, and common broker extension points.

## Important APIs, types, and functions
- Global settings control DB preallocation, query logging, broker timeout, pickle protocol, pending-file cap, SQLite argument limit, and reclaim page size.
- `native_str_keys_and_values()`, `zero_like()`, `dict_factory()`, and `chexor()` are shared data helpers.
- `_db_timeout()` retries locked SQLite operations under `LockTimeout` with eventlet sleeps and exponential backoff.
- `DatabaseConnectionError` and `DatabaseAlreadyExists` provide contextual SQLite errors.
- `GreenDBConnection` and `GreenDBCursor` wrap SQLite operations so `execute()` and `commit()` cooperate with eventlet during lock waits.
- `get_db_connection()` opens a configured SQLite connection, detects accidental empty DB creation, sets pragmas, row/text factories, trace logging, and the SQL `chexor` function.
- `TombstoneReclaimer` deletes old tombstones in bounded name-ordered batches and reports remaining newer tombstones.
- `DatabaseBroker` is the core base class for account/container brokers, with extension points `_initialize()`, `_newid()`, `_is_deleted()`, `empty()`, `_commit_puts_load()`, `merge_items()`, and `make_tuple_for_pickle()`.

## Control flow
Database creation uses a temporary file in the target DB directory, fast unsafe SQLite pragmas for schema setup, common incoming/outgoing sync tables and triggers, subclass initialization, commit, fsync, parent-directory lock, atomic rename, and then a normal configured connection. Existing DB connections are opened lazily by `get()`, which yields the connection, rolls back after use to close any implicit transaction, and quarantines malformed/corrupt/disk-error databases.

Writes to account/container item tables may be deferred through `put_record()`. It locks the pending file's parent directory, appends a colon-delimited base64 pickle of a subclass-defined tuple when below `PENDING_CAP`, or commits immediately when the pending file is large. `_commit_puts()` preallocates if enabled, decodes pending entries with Swift's safe unpickle helper, delegates to subclass item merging, truncates the pending file, and can include an additional immediate item. Read paths call `_commit_puts_stale_ok()` first unless commits are skipped or stale reads are allowed.

Replication helpers expose row iteration since a ROWID, sync-point get/list/merge operations, max row lookup, replication info, database ID regeneration after rsync, and timestamp merging. Metadata helpers load JSON metadata, apply timestamp-wins updates, lazily add the metadata column to older DBs, validate account/container metadata limits, clear metadata during delete, and reclaim old empty metadata. Reclaim deletes old tombstones in pages, deletes old sync rows when schema supports `updated_at`, and returns a `TombstoneReclaimer` for accounting.

## State and persistence behavior
This module is heavily persistent. It creates and mutates SQLite DB files, `.pending` files, sync tables, stat tables, metadata JSON columns, and tombstone rows. It uses atomic rename for DB creation, parent-directory locks for creation and pending commits, fsync for newly initialized DB files, optional fallocate preallocation, and quarantine renames of corrupt DB directories under `<device>/quarantined/<db_type>s/`. Pending files are append-only until committed and truncated.

## Dependencies and integration points
The broker base depends on eventlet concurrency (`sleep`, `Timeout`), SQLite, Swift constraints and UTF-8 validation, safe pickle loading, filesystem utilities (`renamer`, `mkdirs`, `lock_parent_directory`, `fallocate`, `md5`), timestamp classes, `LockTimeout`, and `HTTPBadRequest`. Account and container backend brokers subclass `DatabaseBroker` to define schema, item merge semantics, deletion rules, and pending pickle formats. Replicators, auditors, servers, and sharding code rely on its connection and replication contracts.

## Risks and edge cases
SQLite locking behavior is central: ungreened `executemany` and `executescript` are explicitly not wrapped, and code using them can block eventlet. `get()` temporarily removes `self.conn` while yielding; nested use must go through `maybe_get()` or separate broker instances. Stale reads can hide pending-file commit failures when `stale_reads_ok=True`. Pending files use pickle data, mitigated by Swift's unpickle helper but still a format requiring care. The accidental DB creation detector compares file size and ctime after `sqlite3.connect`; filesystem timestamp behavior can affect it. Metadata updates compare internal timestamp strings lexically, so callers must provide normalized timestamps. Quarantine moves whole DB directories and raises a new database error, which is correct for corruption but disruptive if false-positive strings appear in unrelated errors.

## Test signals
Tests should cover green retry behavior under locked DBs, accidental create detection, schema initialization and atomic rename, pending append/commit/truncate paths, invalid pending entries, stale read behavior, skip-commit rejection, metadata update timestamp precedence and validation, metadata column migration, delete timestamp/status updates, quarantine trigger strings, tombstone reclaim batching, sync-point merge semantics, `newid()` after rsync, reclaimable-state rules, preallocation thresholds, and subclass extension contracts.
