# sources/storage-engines/wiredtiger/test/model/src/include/model/kv_transaction_snapshot.h

Purpose: declares snapshot polymorphism used to decide whether an update is visible to a transaction or checkpoint.

Important APIs and types: abstract `kv_transaction_snapshot` with virtual `contains(const kv_update &)`. `kv_transaction_snapshot_by_exclusion` stores `exclude_after` plus a set of excluded transaction IDs. `kv_transaction_snapshot_wt` stores WT write generation, min/max transaction IDs, and excluded WT snapshot IDs. Alias `kv_transaction_snapshot_ptr`.

Control flow: database snapshot creation returns one of these implementations. Reads call `snapshot->contains(update)`. Exclusion snapshots hide updates from transactions newer than the snapshot boundary or explicitly active/excluded. WT snapshots emulate WiredTiger visibility using write generation and WT transaction metadata imported from debug logs.

State and persistence: snapshots are immutable value objects held by transactions and checkpoints. They do not mutate database state, but they preserve a point-in-time view even after active transactions change.

Dependencies and integration: includes `core.h` and forward-declares `kv_update`. Used by `kv_database`, `kv_transaction`, `kv_checkpoint`, `kv_table_item`, and debug-log parser.

Risks: snapshot correctness depends on `kv_update` retaining model transaction IDs and optional WT transaction metadata after commit. Imported WT snapshots need accurate write generation, min/max, and exclusion lists. A wrong `contains` implementation would affect all visibility, checkpoint, and RTS behavior.

Test signals: tests should create concurrent transactions with active exclusions, verify snapshot reads before and after commits, compare WT debug-log imported visibility, and cover checkpoint snapshots with committed and active transactions.
