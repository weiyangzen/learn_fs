# sources/storage-engines/foundationdb/fdbserver/workloads/SkewedReadWrite.cpp

## Purpose
`SkewedReadWriteWorkload` extends `ReadWriteCommon` to concentrate read and optional write traffic on shards owned by rotating subsets of storage servers. It creates server-local hot spots and records read/write latency under skewed placement-aware load.

## Important APIs, Types, And Functions
It derives from `ReadWriteCommon` and registers as `SkewedReadWrite`. Important state includes `hotServerFraction`, `hotServerShardFraction`, `hotServerReadFrac`, `hotServerWriteFrac`, `hotReadWriteServerOverlap`, `serverShards`, `serverInterfaces`, and `currentHotRound`. Core methods are `updateServerShards`, `convertKeyBoundaryToIndexShard`, `setHotServers`, `getRandomKeyFromHotServer`, `getRandomKey`, `readOp`, `startReadWriteClients`, and `randomReadWriteClient`.

## Control Flow
`start` optionally starts latency tracing, builds the current storage-server-to-index-range map by reading system server lists and server key ranges, then runs `skewRound` rounds. Each round chooses a contiguous rotating set of hot servers, starts read/write client actors for the round duration, clears clients, waits five seconds, and refreshes shard ownership. Clients issue Poisson-paced transactions, choose reads and writes from hot or uniform key distributions, measure GRV/read/commit/total latency, and retry on errors.

## State And Persistence Behavior
The workload writes values through ordinary read/write transactions inherited from `ReadWriteCommon`. It reads system keyspace with `READ_SYSTEM_KEYS` to derive shard placement. Hot server state is in-memory and recomputed between rounds. Metrics and latency sketches are updated during transactions.

## Dependencies And Integration Points
It depends on `ReadWriteWorkload`, `BulkSetup`, `WorkerInterface`, server key system ranges, storage server interface decoding, `RunRYWTransaction`, latency metric helpers, and `TDMetric`. It includes a unit test for `keyForIndex`/`indexForKey` round-tripping.

## Risks And Edge Cases
`convertKeyBoundaryToIndexShard` asserts that every shard range contains at least one workload key in both forward and reverse reads; empty shards in the workload range would assert. `hotServerCount` is `ceil(fraction * serverShards.size())`, so an empty `serverShards` vector would be invalid. Traffic skew depends on current shard map consistency and can be disrupted by data movement.

## Test Signals
Metrics inherited from `ReadWriteCommon` include read, commit, GRV, retry, transaction class, and latency signals. The unit test `/KVWorkload/methods/ParseKeyForIndex` asserts index parsing correctness for normal and non-overlapping key encodings.
