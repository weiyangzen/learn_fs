# sources/storage-engines/foundationdb/fdbserver/storageserver/StorageServerUtils.h

Purpose: declares move-in shard metadata, move-in phase states, throughput limiting, and persistent key helper APIs for storage-server physical shard movement.

Important APIs and types: `MoveInPhase` enumerates pending, fetching, ingesting, applying updates, read-write pending, complete, cancel, and error. `MoveInShardMetaData` stores shard id, data move id, key ranges, create/high-watermark versions, phase, checkpoints, optional error, start time, and bulk-load flag. It exposes constructors, ordering by first range begin, phase helpers, destination shard id formatting, `toString`, and serialization. `ThroughputLimiter` exposes `ready`, `addBytes`, and `settle`. Free functions declare move-in key/value encoders.

Control flow, state, and persistence: metadata is serializable persistent state used to resume move-in work. The limiter state is in-memory timing and byte accounting.

Dependencies and integration: depends on FDB key/version/UID types, Flow futures/time, deterministic random IDs, and checkpoint metadata. Storage-server actor code uses these helpers when fetching physical shards and applying updates.

Risks and test signals: risks are phase enum compatibility, omitted `error`/`startTime` from serialization, empty `ranges` in `operator<`, and high-watermark correctness. Tests should cover serialization compatibility, constructor defaults, phase transitions, and key helper round-trips.
