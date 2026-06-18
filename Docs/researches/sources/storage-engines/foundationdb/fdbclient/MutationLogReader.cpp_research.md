# sources/storage-engines/foundationdb/fdbclient/MutationLogReader.cpp

## Purpose

`MutationLogReader.cpp` implements the actor-side logic for reading backup/restore mutation log key ranges in strictly version-ordered chunks. Mutation logs are sharded by a one-byte hash prefix; the reader runs 256 `PipelinedReader` instances, one per hash value, reads each hash range with bounded pipeline depth, and merges their results with a priority queue ordered by the first version in each block. Consumers call `MutationLogReader::getNext()` to receive non-empty `RangeResultRef` slices until `end_of_stream`.

## Important APIs, types, and functions

The file-local helpers `versionToKey()` and `keyRefToVersion()` encode and decode a `Version` as an eight-byte big-endian suffix under a caller-provided key prefix. This encoding is the ordering contract that makes ordinary FoundationDB key-range reads produce version-ordered records inside each hash shard.

`mutation_log_reader::RangeResultBlock::consume()` returns a `Standalone<RangeResultRef>` slice from the current block and advances `indexToRead`. It cuts the block at `stopVersion`, defined as the lesser of `lastVersion` and the next `CLIENT_KNOBS->LOG_RANGE_BLOCK_SIZE` boundary after `firstVersion`, plus one. If the block is not exhausted, it updates `firstVersion` to the next unread item. This chunking ensures the merge step does not emit a long range from one hash that might hide lower-version records still buffered in another hash.

`mutation_log_reader::PipelinedReader::startReading()` starts the asynchronous read loop. `getNext()` delegates to static actor `getNext_impl()`. The read loop holds a `FlowLock` token for each outstanding read, issues system-key and lock-aware range reads from the current begin version to the end version, sends non-empty `RangeResultBlock` objects to its `PromiseStream`, sends `end_of_stream()` when the shard is exhausted, and releases pressure only when the consumer calls `release()`.

`MutationLogReader::initializePQ()` waits for one block, or stream end, from each of the 256 hash readers. It initializes the priority queue with every non-empty first block and increments `finished` for readers that are already empty.

`MutationLogReader::getNext()` delegates to static actor `getNext_impl()`. That actor repeatedly pops the lowest first-version block, consumes an ordered slice, either releases the corresponding hash reader and awaits its next block or pushes the partially consumed block back, and returns the first non-empty slice. When all 256 readers are finished, it waits for every reader actor to finish and throws `end_of_stream()`.

`forceLinkMutationLogReaderTests()` exists as a link anchor so the unit test in this compilation unit can be forced into test binaries.

## Control flow

Construction of `MutationLogReader` happens in the header: it builds a prefix from `beginKey + uid`, constructs 256 `PipelinedReader` instances with hash-specific prefixes, and starts them if pipeline depth is positive. `Create()` then calls `initializePQ()` before returning the reference, so a created reader is ready to emit globally ordered data or report end-of-stream.

Each `PipelinedReader` computes `begin = versionToKey(currentBeginVersion, prefix)` and `end = versionToKey(endVersion, prefix)`. It repeatedly takes a pipeline token, sets `ACCESS_SYSTEM_KEYS` and `LOCK_AWARE`, and performs `tr.getRange(KeyRangeRef(begin, end), limits)`. Limits use unlimited rows and either `BACKUP_SIMULATED_LIMIT_BYTES` for non-speedup simulation or `BACKUP_GET_RANGE_LIMIT_BYTES` otherwise. Non-empty results are wrapped with first/last decoded versions and sent to the stream. If `kvs.more` is false, it sends stream end and returns. Otherwise it advances `begin` to `kvs.getReadThrough()` and loops. `transaction_too_old` triggers `fullReset()` without delay because the transaction is intentionally reused until it ages out; other errors go through `tr.onError(err)`.

The merge actor keeps at most one block per hash in the priority queue. After popping a block, it calls `consume()`. If the block is empty, it releases the associated reader's `FlowLock` token, waits for another block from that reader, and pushes it or records completion. If the block still has unread items, it is pushed back with its updated `firstVersion`. Empty slices are skipped, so callers only see useful ranges.

## State and persistence behavior

The reader does not persist state outside process memory. Ordering state lives in `RangeResultBlock::{firstVersion,lastVersion,indexToRead}`, per-shard read state lives in `PipelinedReader::{prefix,endVersion,currentBeginVersion,readerLimit,reads,reader}`, and global merge state lives in `MutationLogReader::{pipelinedReaders,priorityQueue,finished}`. The actual mutation log data remains in FoundationDB system key ranges; this code only streams ranges and carries arenas forward in returned `Standalone<RangeResultRef>` values.

`currentBeginVersion` is initialized in the header and used to compute the first read key. In this implementation the loop advances the local `begin` key with `getReadThrough()` rather than updating the member, so the member is construction-time state for the active actor.

## Dependencies and integration points

The implementation depends on `fdbclient/MutationLogReader.h`, `NativeAPI.actor.h` through the header for `Database` and `Transaction`, Flow actors/futures, `FlowLock`, `PromiseStream`, `RangeResult`, FoundationDB transaction options for system-key and lock-aware reads, `CLIENT_KNOBS` backup/log constants, and simulator globals to adjust byte limits.

Its main integration point is the backup/restore mutation log keyspace. The header comments identify prefixes such as `\xff\x02/alog/UID/hash/` for restore and `\xff\x02/blog/UID/hash/` for backup. The fdbserver workload `MutationLogReaderCorrectness.cpp` and `tests/fast/MutationLogReaderCorrectness.toml` reference this component as an integration test signal.

## Risks and edge cases

The correctness of global ordering depends on every key having the expected prefix plus eight-byte big-endian version suffix. `keyRefToVersion()` directly casts the suffix bytes to `uint64_t*` before endian conversion; malformed or too-short keys would be unsafe, so callers must restrict ranges to mutation-log keys.

`initializePQ()` serially awaits the first result from all 256 readers. A stuck shard can delay reader creation even if other shards have data. Pipeline depth zero creates no readers but `finished` starts at zero in the main constructor; callers should use a positive pipeline depth.

Backpressure depends on `readerLimit.release()` being called only after a block is fully consumed. A consumer that stops calling `getNext()` leaves reader actors blocked or buffered. Error propagation from a shard stops the merged reader except for `end_of_stream`, and transaction retry behavior must remain compatible with reading system key ranges over potentially long backup intervals.

The version-boundary slicing in `consume()` is central and non-obvious. Changes to `LOG_RANGE_BLOCK_SIZE` or to mutation log key layout can affect whether the priority queue merge remains strictly ordered without over-buffering.

## Test signals

The local unit test `/fdbclient/mutationlogreader/VersionKeyRefConversion` validates round-trip conversion for zero, positive, negative, minimum, and maximum `int64_t` versions under a prefix. The workload `MutationLogReaderCorrectness` is the higher-level signal for ordered streaming behavior across the 256 hash readers. Useful additional coverage would include empty shards, mixed empty/non-empty shards, partial block consumption around `LOG_RANGE_BLOCK_SIZE` boundaries, transaction retry paths, and simulated byte-limit behavior.
