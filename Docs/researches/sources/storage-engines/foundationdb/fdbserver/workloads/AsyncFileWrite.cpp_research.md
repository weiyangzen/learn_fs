# sources/storage-engines/foundationdb/fdbserver/workloads/AsyncFileWrite.cpp

## Purpose
`AsyncFileWrite.cpp` implements the `AsyncFileWrite` throughput workload. It issues batches of parallel asynchronous writes, syncs between batches, supports sequential wrapping or random offsets, and reports write throughput plus CPU utilization.

## Important APIs, Types, and Functions
- `AsyncFileWriteWorkload`: registered workload with `NAME = "AsyncFileWrite"`.
- Options: `numParallelWrites`, `writeSize`, `fileSize`, `sequential`, plus inherited async file options.
- `_setup`: aligns write size for unbuffered IO, allocates one write buffer, opens the file, and records actual size when nonzero.
- `_start`: runs `runWriteTest` under `testDuration`, records CPU utilization, and drains write futures.
- `runWriteTest`: submits `numParallelWrites` writes, waits for all, waits for previous sync, starts a new sync, clears futures, and updates `bytesWritten`.

## Control Flow
Setup creates a shared zeroed write buffer. Sequential mode opens with initial size zero but keeps the configured target size for wrapping; non-sequential mode opens with the configured file size. The write loop starts at `offset = fileSize`, submits uncancellable writes protected by `holdWhile`, then advances or randomizes offsets. After each batch it waits for writes, chains syncs so the previous sync completes before starting the next, clears the futures, and accounts bytes.

## State and Persistence Behavior
The workload mutates the target file but does not verify contents. The write buffer is reused for all outstanding writes and remains safe because it is not modified while writes are active. `bytesWritten` counts configured write size times parallelism rather than the exact write lengths. Temporary file behavior is inherited from `AsyncFileHandle`.

## Dependencies and Integration Points
The file depends on tester workload infrastructure, `ActorCollection`, `SystemMonitor`, `IAsyncFile`, and `AsyncFile.h`. It uses Flow `timeout`, `waitForAll`, `uncancellable`, and `holdWhile`.

## Risks
In sequential mode, the first write is submitted at offset equal to `fileSize` before offset wraparound; the actual length can be zero because `fileSize - offset` is zero. That is a notable throughput-semantics risk. `numParallelWrites == 0` produces no useful load. Random offset selection assumes nonzero file size. Accounting may overstate actual bytes near EOF. Shared buffer reuse is safe only while the buffer remains immutable.

## Test Signals
Metrics include `Bytes written/sec` and average CPU utilization. The inherited check returns true. Setup/start exceptions are the main failure signal. Registered as `AsyncFileWriteWorkloadFactory`.
