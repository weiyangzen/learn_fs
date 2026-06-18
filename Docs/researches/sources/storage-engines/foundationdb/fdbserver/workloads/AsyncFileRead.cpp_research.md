# sources/storage-engines/foundationdb/fdbserver/workloads/AsyncFileRead.cpp

## Purpose
`AsyncFileRead.cpp` implements the `AsyncFileRead` throughput workload. It opens or creates a file, optionally fills/resizes it, issues parallel reads or mixed read/write operations, supports batched and unbatched modes, and reports throughput and CPU utilization.

## Important APIs, Types, and Functions
- `IOLog` and `ProcessLog`: rolling trace metrics for issue rate, completion rate, and latency split by read/write.
- `AsyncFileReadWorkload`: options `numParallelReads`, `readSize`, `fileSize`, `unbatched`, `sequential`, `writeFraction`, `randomData`, and `fixedRate`.
- `_setup`: aligns read size for unbuffered IO, allocates buffers, opens/fills file, and records actual file size.
- `_start`: runs the test under `testDuration`, records CPU utilization, and drains outstanding futures.
- `readLoop`: unbatched per-buffer loop with optional Poisson pacing and optional writes.
- `runReadTest`: starts unbatched loops or repeatedly issues batched reads.

## Control Flow
Setup prepares buffers and uses `openFile` with read-write/create flags. In unbatched mode, each read buffer gets an independent actor that optionally rate-limits, chooses an offset, optionally writes based on `writeFraction`, logs timing, waits uncancellably, and accounts bytes. In batched mode, the workload issues `numParallelReads` reads, waits for all, accounts bytes, clears futures, and yields. Sequential mode advances and wraps through the file; random mode chooses offsets, page-aligned for unbuffered IO.

## State and Persistence Behavior
The target file is managed by `AsyncFileWorkload`; unbatched mixed mode may mutate it with writes. There is no content oracle. `readBuffers` and `fileHandle` are preserved during IO with `holdWhile`. `bytesRead` counts requested bytes, not actual returned bytes. `ioLog` exists during unbatched mode and emits rolling metrics every five seconds.

## Dependencies and Integration Points
The workload depends on tester infrastructure, `ActorCollection`, `SystemMonitor`, `IAsyncFile`, `AsyncFile.h`, `DeterministicRandom`, Flow `poisson`, `uncancellable`, and `holdWhile`.

## Risks
`randomData` is read but not used; write operations always fill with `RandomByteGenerator`. Offset selection assumes nonzero file size. `ioLog` deletion is unreachable during normal infinite unbatched execution unless cancellation unwinds differently. Byte accounting uses requested size and can overstate near EOF. Mixed read/write mode is performance-only and does not validate contents.

## Test Signals
Metrics include `Bytes read/sec` and average CPU utilization. `IOLog` emits `ProcessLog` trace events for issue/completion/duration rates and latencies. Success is inherited from `AsyncFileWorkload::check` unless setup/start throws.
