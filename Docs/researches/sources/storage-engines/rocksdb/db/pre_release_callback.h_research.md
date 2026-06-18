# sources/storage-engines/rocksdb/db/pre_release_callback.h

## Purpose
`pre_release_callback.h` declares `PreReleaseCallback`, an internal write-thread hook invoked after WAL writing and before memtable writing/sequence-number release. It lets RocksDB perform ordered side effects on the write thread before a write becomes visible.

## Important APIs, Types, And Functions
`PreReleaseCallback` is an abstract class with a virtual destructor and pure virtual:

`Status Callback(SequenceNumber seq, bool is_mem_disabled, uint64_t log_number, size_t index, size_t total)`.

Parameters provide the sequence number to be released, whether the memtable is disabled, the WAL log number when nonzero, the callback's index within the write group, and the total callbacks in the group. The index/total pair lets implementations reduce redundant group-level work.

## Control Flow
The write thread calls callbacks after WAL write and before memtable write. If a callback returns non-OK, the sequence number is not released and the same status is propagated to all writers in the write group.

## State And Persistence Behavior
The callback itself has no storage in this header, but implementations can update external state while write ordering is serialized by the write thread. Because the WAL may already contain the write, failure handling must preserve recovery and visibility semantics.

## Dependencies And Integration Points
The header depends on `rocksdb/status.h` and `rocksdb/types.h`. It integrates with write groups, WAL logging, memtable-disabled queues, sequence-number release, and transaction/write-prepared modes.

## Risks
This hook is on a critical write-path latency and correctness boundary. A failing callback affects every writer in the group. Misusing `index`/`total` can duplicate or omit group-level work. The `is_mem_disabled` flag is described as debug-oriented, so production logic should not overfit to it unless the write queue contract guarantees it.

## Test Signals
Relevant signals are callback invocation order after WAL and before memtable/sequence release, correct propagation of callback failure to all grouped writers, unreleased sequence numbers on failure, and correct log-number/index/total values.
