# sources/storage-engines/rocksdb/utilities/fault_injection_fs.h

## Purpose
This header defines `FaultInjectionTestFS`, a `FileSystemWrapper` used by RocksDB tests and stress tools to simulate filesystem failures, crash-related unsynced data loss, metadata failures, read corruption/truncation, and special file-open contract checks. It also defines wrapper file classes for writable, random-access, random-RW, sequential, and directory objects so faults can be injected at individual filesystem API boundaries.

## Important APIs, types, and functions
`InjectedErrorLog` is a fixed-size thread-safe circular log for recently injected faults. It records timestamp, hashed thread id, and formatted context, and provides `PrintAll()` using async-signal-safe Unix syscalls when possible. `HexHead()` formats a short data prefix for diagnostic messages.

`fault_injection_detail` contains deferred detail builders such as `SizeAndHead`, `OffsetSizeAndHead`, `Count`, and `ReqOffsetAndSize`. These return lambdas evaluated only when a fault is actually injected.

`FaultInjectionIOType` partitions injection into read, write, metadata read, and metadata write. `FSFileState` tracks a file name, last appended offset, last synced offset, and buffered unsynced data, with methods to drop all or random unsynced data.

`TestFSWritableFile` wraps `FSWritableFile` and intercepts `Append`, `PositionedAppend`, `Truncate`, `Flush`, `Sync`, `RangeSync`, `Close`, and `GetFileSize`. It tracks per-file state under a mutex and reports appended, synced, opened, and closed transitions back to `FaultInjectionTestFS`.

`TestFSRandomRWFile`, `TestFSRandomAccessFile`, `TestFSSequentialFile`, and `TestFSDirectory` wrap the corresponding filesystem abstractions and inject write/read/metadata faults. Random-access and sequential wrappers also coordinate with `ReadUnsynced()` so tests can choose whether readers see unsynced data from open writers.

`FaultInjectionTestFS` exposes overrides for most `FileSystem` entry points: file creation/opening, deletion, renaming, linking, metadata queries, directory creation, file-size and free-space queries, async polling, and aborts. Test controls include `SetFilesystemActive`, `SetFilesystemDirectWritable`, `SetInjectUnsyncedDataLoss`, `SetReadUnsyncedData`, `SetAllowLinkOpenFile`, `SetThreadLocalErrorContext`, `Enable/DisableThreadLocalErrorInjection`, file-type and IO-activity exclusions, corruption-before-write toggles, checksum handoff controls, and failure flags for unique id and SST file size APIs.

## Control flow
Normal operations first pass through `FaultInjectionTestFS` validation and `MaybeInjectThreadLocalError()`. If the filesystem is inactive, wrappers return the stored `fs_error_` for operations that should fail during simulated outage/reset. If thread-local injection is enabled and not excluded by IO activity or file type, the relevant `ErrorContext` decides using `Random::OneIn(one_in)` whether to return an injected status or mutate read output.

Writable operations update `FSFileState`: append-style calls advance `pos_at_last_append_` and optionally buffer data for unsynced-loss simulation; sync-style calls advance `pos_at_last_sync_`; close reports final state and prevents repeated raw `Close()` forwarding after the first wrapper close attempt. Directory sync removes entries from `dir_to_new_files_since_last_sync_`.

Read wrappers can consult `ReadUnsynced()` to splice buffered unsynced bytes into scratch or to restrict visible size to synced data when deprecated `read_unsynced_data_` is false. Metadata operations use metadata injection types and can also be forced to report no free space when the inactive filesystem error has `kNoSpace`.

## State and persistence behavior
Persistent simulated state is in memory inside `FaultInjectionTestFS`: `db_file_state_`, `open_managed_files_`, `file_open_contracts_`, `dir_to_new_files_since_last_sync_`, filesystem flags, exclusion sets, thread-local error contexts, corruption and checksum flags, and the injected-error log. It does not persist across process lifetime, but it models what would survive a crash by tracking synced offsets and directory sync state. `DropUnsyncedFileData()`, `DropRandomUnsyncedFileData()`, and `DeleteFilesCreatedAfterLastDirSync()` mutate the underlying target filesystem to reflect simulated recovery.

## Dependencies and integration points
The header depends on RocksDB filesystem abstractions (`rocksdb/file_system.h`), filename parsing (`file/filename.h`), mutex utilities, `Random`, `ThreadLocalPtr`, `Env::IOActivity`, file types, checksum types, `Slice`, `IOStatus`, and platform syscalls for diagnostic printing. It is integrated into db/crash/stress tests by wrapping an existing `FileSystem` and being installed in `Env` or `DBOptions`.

## Risks and edge cases
The injected-error log intentionally accepts benign races while printing signal-safely. Thread-local contexts own callstack memory and must be swapped/deleted carefully. File-open contract tracking and link-open hygiene can reject flows that the underlying filesystem would allow. `read_unsynced_data_` has deprecated semantics and can mask POSIX-like visibility differences. Fault injection can mutate read buffers, truncate slices, or return OK while counting a fault, so callers must not assume all injected faults are non-OK statuses.

## Test signals
`fault_injection_fs_test.cc` directly covers `InjectedErrorLog`, info-log exclusion behavior across read/write/metadata operations, and the writable-file close retry contract. Broader coverage is likely in RocksDB crash, stress, and DB tests that use this wrapper to force filesystem failures and recovery scenarios.
