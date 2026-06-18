# sources/storage-engines/pebble/sstable/write_queue.go

## Purpose
Implements the asynchronous write queue used by row-format SSTable writing to preserve write ordering while allowing data block compression to happen separately.

## Important APIs, Types, And Functions
`writeTask` carries compressed data block buffers, index block state, separator keys, inflight size accounting, and a reusable `compressionDone` channel. `writeQueue` owns a task channel, worker goroutine, writer pointer, error state, and close flag. Methods include `clear`, `newWriteQueue`, `performWrite`, `releaseBuffers`, `runWorker`, `addSync`, and `finish`.

## Control Flow
Compression producers enqueue tasks whose `compressionDone` channel is signaled when physical block bytes are ready. The queue worker waits for that signal, writes the precompressed data block, adds the corresponding index entry, records the first error, and releases pooled buffers/tasks. `addSync` performs the same flow inline before asynchronous queue use. `finish` closes the channel and waits for the worker.

## State And Persistence Behavior
Persistent effects are data block writes and index entries through `RawRowWriter.layout` and `addIndexEntry`. Queue state is transient and manages buffer/task pool ownership.

## Dependencies And Integration Points
Integrated with `RawRowWriter`, `dataBlockBuf`, `indexBlockBuf`, block handles/properties, and writer pools. Depends on `sync`.

## Risks And Edge Cases
Task channel reuse requires compression signals to be drained before pooling. Once an error occurs, later blocks skip writes but still release buffers. `addSync` is valid only before asynchronous `add` usage, per comment.

## Test Signals
Covered indirectly by writer round-trip, fixture byte equality, and final-block tests.
