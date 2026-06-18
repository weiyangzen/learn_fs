# sources/storage-engines/foundationdb/fdbrpc/AsyncFileWriteChecker.h

## Purpose
`AsyncFileWriteChecker.h` implements an `IAsyncFile` wrapper that records checksums for recently written full pages, then continuously reads synced pages back to detect lost or corrupted writes.

## Important APIs, Types, and Functions
The primary type is `AsyncFileWriteChecker`. It forwards most `IAsyncFile` methods while instrumenting `read`, `readZeroCopy`, `write`, `truncate`, and `sync`. `WriteInfo` stores CRC32C and millisecond timestamp. The nested `LRU` stores page-to-write-info history with maps for page order and truncation support. Private actors `sweep` and `runChecksumLogger`, plus helpers `verifyChecksum` and `updateChecksumHistory`, implement verification and logging.

## Control Flow
Writes compute CRC32C for each fully covered checker page, reserve global history budget, insert those pages into the LRU, mark them as actively writing, then erase the writing marks when the underlying write completes. Reads compute page checksums over full pages and compare them against stored history only for pages written before the last successful `sync`. `sync` forwards to the wrapped file and updates `syncedTime` after success. `sweep` repeatedly chooses the least-recently-used page, skips invalid or currently writing pages, and reads it through the wrapper path so successful verification removes it.

## State and Persistence Behavior
The wrapper's persistent state is in memory: wrapped file reference, page buffer, LRU checksum history, global optional budget, `syncedTime`, active-writing set, counters, and background actors. It does not persist metadata to disk. It only treats pages as eligible for verification after sync, matching durability expectations. Truncate removes history at and beyond the new full-page boundary and refunds budget.

## Dependencies and Integration Points
It depends on `flow/IAsyncFile.h`, CRC32C, Flow knobs, trace events, deterministic randomness for LRU sampling, and Valgrind annotations. It can wrap any `IAsyncFile` implementation and is useful for simulation or diagnostic configurations that need lost-write detection.

## Risks and Edge Cases
Only full checker pages are tracked; partial-page writes or reads are skipped. `readZeroCopy` casts `data` rather than `*data` when verifying, which appears suspicious for zero-copy buffers. `syncedTime` is not explicitly initialized in the constructor before first sync, so pre-sync reads rely on default object initialization behavior. The `sweep` actor loops forever and may repeatedly delay if no page is available. Budget exhaustion skips remaining pages in an update range, reducing detection coverage. The class assumes all operations run in Flow's single-threaded event context.

## Test Signals
The companion `.cpp` file tests LRU behavior. Runtime signals include `AsyncFileLostWriteDetected`, periodic `AsyncFileWriteChecker` trace events, success/failure counters, and simulation workloads that enable page write checksum history.
