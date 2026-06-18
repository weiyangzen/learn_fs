# sources/storage-engines/foundationdb/fdbserver/workloads/AsyncFileCorrectness.cpp

## Purpose
`AsyncFileCorrectness.cpp` implements the `AsyncFileCorrectness` workload. It stress-tests `IAsyncFile` read, write, sync, reopen, and truncate behavior against an in-memory file model while supporting multiple outstanding operations and byte-level locks.

## Important APIs, Types, and Functions
- `OperationType`: `READ`, `WRITE`, `SYNC`, `REOPEN`, `TRUNCATE`.
- `OperationInfo`: buffer, offset, length, flush flag, operation type, and slot index.
- `AsyncFileCorrectnessWorkload`: options `maxOperationSize`, `numSimultaneousOperations`, and `targetFileSize`; state for live operations, memory file, locks, validity mask, success, CPU metrics, and operation counter.
- `_setup`: allocates model/lock/mask arrays and opens/creates the file.
- `runCorrectnessTest`: schedules operations, validates reads, handles postponed flush operations, and replaces completed slots.
- `generateOperation`, `checkFileLocked`, `processOperation`, and `updateMemoryBuffer`.

## Control Flow
Setup creates the memory model and opens the file. Start runs the correctness loop until `testDuration`, records CPU utilization, and drains outstanding IO for up to ten seconds. The loop keeps up to `numSimultaneousOperations` operations active unless a flush operation is pending. Reads and writes are generated only where byte locks permit; `REOPEN` and `TRUNCATE` set `flushOperations` and are run serially after active operations drain.

`processOperation` performs uncancellable reads/writes/truncates with `holdWhile` protection. Writes update the memory model and validity mask before issuing IO, then extend expected `fileSize` as needed. Reads verify byte counts and compare known ranges, learning unknown ranges from file contents. Reopen checks that size did not shrink or grow by a full page. Truncate verifies reported size and resizes model structures.

## State and Persistence Behavior
The real file is the persistent target. `memoryFile` mirrors expected bytes, `fileLock` uses `0xFFFFFFFF` for writes and read counts otherwise, and `fileValidityMask` tracks which bytes are known. `fileSize` is expected logical size. `targetFileSize` can be increased when operation size and concurrency would make locking too dense. `success` latches failure.

## Dependencies and Integration Points
The workload depends on `AsyncFile.h`, Flow random, `IAsyncFile`, `ActorCollection`, `SystemMonitor`, `uncancellable`, `holdWhile`, and tester `WorkloadFactory`.

## Risks
The read validation branch appears to compare `fileValidityMask` bytes with returned data where `memoryFile` was likely intended; this is a high-value review target. Byte-level locks are precise but expensive. Signed/unsigned arithmetic around `fileSize - info.offset` must be handled carefully. Reopen size tolerance encodes filesystem alignment assumptions. New flush-like operations would need to preserve the postponed-operation drain behavior.

## Test Signals
`check` returns `success`. Failures print incorrect read data/length, reopen size changes, and truncate size mismatches. Metrics include operation count and average CPU utilization. Registered as `AsyncFileCorrectnessWorkloadFactory`.
