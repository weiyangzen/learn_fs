# sources/storage-engines/foundationdb/fdbclient/include/fdbclient/MutationLogReader.h

## Purpose
Declares a parallel mutation-log reader for backup/restore log chunks. It merges 256 hash-partitioned range-read streams into a strictly version-ordered stream of mutation log records.

## Important APIs, Types, And Functions
`mutation_log_reader::RangeResultBlock` wraps one `RangeResult` with first/last version metadata, hash, prefix length, and consumption index. `consume()` returns a partial `RangeResultRef` while preserving strict order boundaries, and `operator<` reverses ordering for a min-heap. `PipelinedReader` owns one hash partition, a prefix, version bounds, pipeline depth, a `FlowLock`, and a `PromiseStream<RangeResultBlock>`. It can start reading, fetch the next range, release a pipeline slot, and expose completion. `MutationLogReader` owns up to 256 `PipelinedReader`s, a priority queue, version range, prefix, pipeline depth, finished count, async `Create()`, and `getNext()`.

## Control Flow
Construction builds a common log prefix from begin key and UID, starts one `PipelinedReader` per hash when pipeline depth is positive, then `Create()` initializes the priority queue with first blocks. Each `PipelinedReader` performs range reads for its hash/version span and streams blocks. `MutationLogReader::getNext()` consumes the earliest block from the heap, returns only the prefix of that block that is safe in global version order, and advances/replenishes readers until all partitions finish.

## State And Persistence Behavior
The reader does not mutate durable state. It reads backup/restore mutation log keyspaces such as `alog` or `blog` under the supplied prefix/UID/hash structure. Runtime state includes the per-hash reader pipeline, priority queue, version bounds, and consumption offsets.

## Dependencies And Integration Points
The header depends on FDB types, NativeAPI, Flow futures, and `ActorCollection` infrastructure. It integrates with backup log reading, restore application, and any code consuming mutation logs in version order.

## Risks And Test Signals
Risks include incorrect version ordering across hash partitions, starvation or deadlock from pipeline lock handling, off-by-one version windows, wrong prefix length parsing, empty block handling, and memory pressure from 256 concurrent readers. Test signals should include deterministic merge ordering across hashes, partial consume boundaries near million-version rounding, pipeline depth zero/nonzero behavior, begin/end version edges, empty partitions, and restore/backup log replay correctness.
