# sources/object-store/garage/src/model/index_counter.rs

## Purpose
This file implements generic eventually replicated counters for indexed metadata tables. It lets tables such as objects, multipart uploads, and K2V items maintain bucket/partition-level counts and byte totals, while using per-node local counter state to avoid non-commutative increments in the global table.

## Important APIs, types, and functions
`CountedItem` defines counter table name, counter partition/sort keys, and `counts()`. `CounterEntry<T>` is the replicated global row mapping metric names to `CounterValue`. `CounterValue` stores per-node `(timestamp, value)` entries. `CounterTable<T>` is a sharded table schema. `IndexCounter<T>` owns the local DB tree and replicated counter table. `IndexCounter::count` updates local counters transactionally when an item changes. `offline_recount_all` zeros old local counters and recounts all entries from a source table. `filtered_values` collapses per-node values, optionally filtering to current layout nodes.

## Control flow
Table `updated` hooks call `IndexCounter::count(tx, old, new)`. The method computes metric deltas by subtracting old counts and adding new counts, loads or creates a local counter row, advances each metric timestamp using `max(previous + 1, now_msec())`, persists the local row, converts it into a global `CounterEntry`, and queues replication. Query-side filtering keeps one value per metric by taking the maximum value among selected nodes.

## State and persistence behavior
Local counters live in DB trees named `local_counter_v2:<COUNTER_TABLE_NAME>`. Global counters live in sharded replicated tables named by `CountedItem::COUNTER_TABLE_NAME`. Tombstones are entries whose selected values are all zero. `offline_recount_all` mutates local and global counter rows in batches of roughly 1000 entries, first zeroing all existing counters and then rebuilding from the counted table.

## Dependencies and integration points
It depends on Garage DB transactions, table replication, CRDT traits, migration codecs, cluster layout helpers, time, and background runners. `Object`, `MultipartUpload`, and `K2VItem` implement `CountedItem`; `Garage::new` creates corresponding counters and table hooks.

## Risks and edge cases
Counter correctness is best-effort: table hooks log and continue on counter failures, so displayed indexes can drift until offline recount. Taking the maximum per-node value assumes local node counters are independent replicated observations, but decommissioned or gateway nodes must be filtered by layout. Recount is an offline repair path and can be expensive. Timestamp monotonicity relies on local persisted timestamps and millisecond time.

## Test signals
No local tests. Useful tests should cover delta calculation, merge conflict resolution by timestamp, filtering by live nodes, tombstone filtering, hook failure behavior, and offline recount against object/MPU/K2V tables.
