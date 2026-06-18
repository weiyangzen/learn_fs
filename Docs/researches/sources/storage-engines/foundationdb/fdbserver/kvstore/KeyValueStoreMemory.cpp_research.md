# sources/storage-engines/foundationdb/fdbserver/kvstore/KeyValueStoreMemory.cpp

## Purpose
`KeyValueStoreMemory.cpp` implements an `IKeyValueStore` backed by an in-memory ordered container plus an `IDiskQueue` mutation/snapshot log. It provides the normal memory store, the radix-tree memory variant, and log-system testing support.

## Important APIs, Types, and Functions
`KeyValueStoreMemory<Container>` implements lifecycle, `getType`, `getSize`, `getStorageBytes`, `set`, `clear`, `commit`, `readValue`, `readValuePrefix`, `readRange`, `resyncLog`, `enableSnapshot`, and `uncommittedBytes`. `OpType` enumerates log records including set, clear, snapshot item/end/abort, commit, rollback, and snapshot delta. `OpQueue` buffers uncommitted mutations. `commit_queue`, `log_op`, `recover`, `fullSnapshot`, `snapshot`, and `commitAndUpdateVersions` are the key internal functions. Factories are `keyValueStoreMemory(...)` and `keyValueStoreLogSystem(...)`.

## Control Flow
Writes go to `queue` unless the transaction is large, in which case they apply directly to `data`. `commit()` waits for recovery, handles replace-content snapshot accounting, either snapshots large transactions or applies/logs queued operations, notifies the background snapshot actor, writes `OpCommit`, commits the disk queue, resets transaction counters, and schedules a pop of the previous snapshot region. Reads wait for recovery and then use the ordered container for point, prefix, forward range, or reverse range reads.

## State and Persistence Behavior
Durable state is a stream of records in `IDiskQueue`: `OpHeader`, key bytes, value/range-end bytes, and a one-byte sentinel. Recovery reads records sequentially. `OpCommit` applies the recovery queue; `OpRollback` discards uncommitted recovery state; short or zero-filled tails are treated as the end unless exact recovery is requested. Snapshot records periodically rewrite the full data set so old log regions can be popped. Snapshot deltas prefix-compress consecutive keys. Memory pressure is tracked through container sums, queued bytes, transaction bytes, and a configured limit.

## Dependencies and Integration Points
The implementation depends on `IDiskQueue`, `IKeyValueContainer`, `RadixTree`, Flow actors, `NotifiedVersion`, server/client knobs, transaction state debug hooks, and `ServerDBInfo`. `openKVStore` selects it for `MEMORY` and `MEMORY_RADIXTREE`; the memory backend opens a V2 XXHash disk queue.

## Risks
Out-of-space behavior returns `Never()` from `commit` and drops later modifications while unavailable. Large transactions change when mutations apply to `data`. Recovery uses packed headers and sentinel bytes; malformed lengths can create large reads if not constrained elsewhere. Snapshot correctness depends on ordering between `notifiedCommittedWriteBytes`, snapshot item writes, and `OpCommit`.

## Test Signals
There are no local `TEST_CASE`s, but trace events and probes cover recovery, skipped zero-fill, exact recovery failure, large transaction mode, many writes at once, full snapshot end, and commit queue size warnings. Indirect tests should cover crash recovery, partial tail repair, snapshot abort/resync, range ordering, radix-tree mode, sequential batching, and memory-limit behavior.
