# sources/storage-engines/rocksdb/utilities/fault_injection_fs.cc

## Purpose
This file implements the modern `FileSystem`-based fault-injection test wrapper. It simulates unsynced data loss, inactive filesystem errors, metadata/data I/O failures, checksum-handoff corruption checks, file-open contract violations, async read failures, and directory fsync durability.

## Important APIs, Types, and Functions
Top-level helpers parse info-log names, split paths, trim directories, and calculate CRC32c/xxHash checksums. `FSFileState` drops buffered unsynced data. `TestFSDirectory` wraps directory fsync/close. `TestFSWritableFile` buffers non-direct writes until sync/range sync, validates write contracts, injects write/metadata errors, checks handoff checksums, and publishes append/sync/close state. `TestFSRandomRWFile`, `TestFSRandomAccessFile`, and `TestFSSequentialFile` wrap random and sequential access with active-state checks and read error injection.

`FaultInjectionTestFS` overrides FileSystem methods for file/directory creation, open, read metadata, write metadata, rename/link, link-count/same-file checks, absolute path, directory checks, poll/abort I/O, and sync-file handling. It also implements state updates, unsynced data dropping, unsynced-data reads, new-file deletion/restore after missing directory fsync, thread-local error injection, and injected-error backtrace printing.

## Control Flow
Writable files created through the wrapper either forward direct/no-loss writes immediately or buffer append data in `FSFileState::buffer_`. `Sync` appends buffered data to the target, clears the buffer, updates `pos_at_last_sync_`, and records state. `RangeSync` flushes a consecutive prefix of buffered data. `Close` records close once, injects metadata errors if configured, drops unsynced buffered data because close is not sync, and closes the target.

Read wrappers call `MaybeInjectThreadLocalError` before forwarding. Sequential reads have extra logic to merge target data with unsynced buffered tail data when `ReadUnsyncedData()` is enabled, handling races where another thread syncs while a read is in progress. `MultiRead` injects per-request errors and optionally an aggregate multiread error.

Filesystem methods first check active state, then inject metadata/read/write errors based on thread-local contexts, then delegate to the target. Creation/open methods validate file-open contracts, wrap returned file objects, and track newly created directory entries. Rename/link propagate file state and open contracts and remember overwritten small-file contents so `DeleteFilesCreatedAfterLastDirSync` can restore preexisting files instead of simply deleting them.

## State and Persistence Behavior
The wrapper maintains tracked file states, open managed files, file-open contracts, unsynced directory entries with previous contents, active/inactive status, error contexts, read/write/metadata injection counters, and an injected-error log. Buffered unsynced writes may not reach the target filesystem until sync. Drop helpers clear unsynced buffers or delete/restore files whose containing directory was not fsynced. Normal operations still mutate the target filesystem when forwarded.

## Dependencies and Integration Points
It depends on the declarations in `fault_injection_fs.h`, composite env wrappers, thread status utilities, stack traces, `IOStatus`, `SyncPoint`, coding/checksum helpers, CRC32c, xxHash, random utilities, string helpers, and RocksDB FileSystem abstractions. It is used by durability, backup, checkpoint, DB stress, and fault-injection tests.

## Risks and Edge Cases
This is a complex test model, not a production filesystem. Direct I/O writes are not buffered for unsynced data loss. `RangeSync` assumes consecutive ranges. Some read-unsynced paths are intentionally TODO for random reads. Close status injection records the wrapper-level close transition before returning an error to model one-shot close semantics. Error injection can corrupt read buffers or return empty results to exercise checksum validation. Contract tracking can return `NotSupported` for reopen/read violations and must be kept in sync across rename/link/delete. Info-log filename parsing is custom because standard file parsing needs log prefixes.

## Test Signals
Strong signals include DB recovery tests after `DropUnsyncedFileData`, directory fsync loss tests, injected read/write/metadata error tests with retryable/data-loss flags, checksum handoff validation, async read failure callbacks, no-readers/no-reopen file-open contract tests, rename/link state propagation, and checkpoint/backup tests that use `FaultInjectionTestFS` to drop unsynced data.
