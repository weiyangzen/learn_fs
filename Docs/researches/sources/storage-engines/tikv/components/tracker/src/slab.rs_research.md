# sources/storage-engines/tikv/components/tracker/src/slab.rs

Purpose: global sharded slab storage for active request trackers, addressed by compact tokens safe against stale key reuse.

Important APIs/types/functions: `GLOBAL_TRACKERS`, `ShardedSlab`, `TrackerSlab`, `TrackerToken`, `INVALID_TRACKER_TOKEN`, and `TrackerTokenArray`.

Control flow: `insert` chooses a shard using a thread-local round-robin counter, inserts into a `slab::Slab`, and builds a token from shard id, sequence, and slab key. `with_tracker` and `remove` validate both key and sequence before returning/mutating a tracker.

State and persistence: process-local 64-shard slab protected by cache-padded `parking_lot::Mutex` values. No durable persistence.

Dependencies/integration: used by TLS tracker propagation and slog serialization of tracker token arrays.

Risks: shard capacity is capped at 4096 and insert failure silently returns `INVALID_TRACKER_TOKEN` after incrementing a metric; sequence bits can wrap eventually, so stale-token protection is probabilistic over very long runtimes.

Test signals: tests cover token bit packing, basic insert/get/remove/iteration, and sharding distribution across threads.
