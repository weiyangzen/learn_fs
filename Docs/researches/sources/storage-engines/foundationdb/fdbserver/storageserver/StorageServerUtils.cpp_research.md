# sources/storage-engines/foundationdb/fdbserver/storageserver/StorageServerUtils.cpp

Purpose: implements helper utilities for storage-server throughput limiting and persistent keys/values used by physical shard move-in state.

Important APIs and functions: `ThroughputLimiter::ready`, `addBytes`, and `settle` implement a simple byte-cap scheduler based on `nextAvailableSec`. `persistMoveInShardsKeyRange`, `persistUpdatesKeyRange`, `persistUpdatesKey`, `decodePersistUpdateVersion`, `persistMoveInShardKey`, `decodeMoveInShardKey`, `moveInShardValue`, and `decodeMoveInShardValue` encode/decode system-key ranges and values for move-in shard metadata and update streams.

Control flow, state, and persistence: `ThroughputLimiter` is in-memory. Move-in helpers define durable key layout under `\xff\xffMoveInShards/` and `\xff\xffMoveInShardUpdates/`; update versions are big-endian to preserve key ordering. Values serialize `MoveInShardMetaData` with versioned object serialization.

Dependencies and integration: depends on Flow time/delay, FDB binary reader/writer, object serialization, UID/version/key types, and `StorageServerUtils.h`. Used by storage-server shard fetch/restore paths.

Risks and test signals: risks are key prefix collisions, endian decode mistakes, limiter time math when cap changes or zero cap, and serialization compatibility. Tests should round-trip UIDs, versions, metadata values, key ranges, and limiter scheduling under positive and disabled caps.
