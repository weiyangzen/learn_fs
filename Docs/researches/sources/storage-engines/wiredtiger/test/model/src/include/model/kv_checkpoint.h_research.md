# sources/storage-engines/wiredtiger/test/model/src/include/model/kv_checkpoint.h

Purpose: defines `kv_checkpoint`, the model snapshot object representing a WT checkpoint's name, transaction snapshot, oldest timestamp, and stable timestamp.

Important APIs and types: constructor `kv_checkpoint(const char *, kv_transaction_snapshot_ptr, timestamp_t, timestamp_t)`, accessors `name()`, `oldest_timestamp()`, `snapshot()`, and `stable_timestamp()`, plus alias `kv_checkpoint_ptr`.

Control flow: `kv_database::create_checkpoint` constructs checkpoints with a snapshot of active transactions and timestamp bounds. Table reads with a checkpoint pass `ckpt->snapshot()` and stable timestamp into `kv_table_item` visibility checks.

State and persistence: checkpoints are immutable after construction and are stored in `kv_database` by name. They model persistent checkpoint visibility rather than owning table data. The stable timestamp is used as the default checkpoint read timestamp; oldest timestamp is retained for metadata comparisons.

Dependencies and integration: includes `core.h` and `kv_transaction_snapshot.h`. Used by `kv_database`, `kv_table`, `kv_table_item`, `verify`, debug-log import, and test checkpoint helpers.

Risks: checkpoint name pointer returned by `name()` is valid only while the object lives. A null or mismatched snapshot would corrupt visibility, but constructor accepts the pointer as provided. Checkpoint semantics rely on the database creating snapshots under the right locks.

Test signals: checkpoint tests should compare model checkpoint reads against WT checkpoint cursors, verify default and named checkpoint behavior, and cover stable timestamp reads and debug checkpoint-read timestamp overrides.
