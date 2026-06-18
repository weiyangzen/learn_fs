# sources/storage-engines/rocksdb/utilities/fault_injection_fs_test.cc

## Purpose
This test file validates targeted behavior in `FaultInjectionTestFS` and `InjectedErrorLog`: safe log recording/printing, circular-buffer wraparound, concurrent recording, byte-prefix formatting, file-type exclusions for info logs, and the rule that an injected metadata-close error must not lead to repeated forwarding of the underlying writable file close.

## Important APIs, types, and functions
`NewFaultFsExcludingInfoLogs()` builds a `FaultInjectionTestFS` over the default environment, excludes `FileType::kInfoLogFile`, installs a thread-local error context for a chosen `FaultInjectionIOType`, and enables that injection type.

`CloseCountingWritableFile` wraps a writable file and increments an external counter in `Close()`, providing an observable signal for whether `TestFSWritableFile` forwards close calls.

The `InjectedErrorLogTest` cases exercise `Record()`, `PrintAll()`, circular wrapping past `kMaxEntries`, concurrent `Record()` calls below wraparound, and `HexHead()`. The `FaultInjectionTestFSTest` cases exercise exclusion filters and close semantics.

## Control flow
The info-log exclusion test creates a DB directory, log directory, old info log, current info log name, and manifest files. It then runs four independent fault filesystems, each with a different injection type. Info-log operations are expected to succeed without incrementing injected error counts, while manifest operations are expected to fail and increment exactly once.

The close retry test creates a real writable file through `FaultInjectionTestFS`, wraps it in `TestFSWritableFile` over a `CloseCountingWritableFile`, injects metadata-write errors, appends data, then calls `Close()` twice and destroys the wrapper. It asserts the injected close error prevents inner close forwarding and later wrapper closes remain no-ops.

## State and persistence behavior
Tests write temporary files under `test::PerThreadDBPath()`. Error counts are stored in per-thread `ErrorContext` instances and read/reset through `GetAndResetInjectedThreadLocalErrorCount()`. `InjectedErrorLog` writes to `/dev/null` in tests, so no diagnostic file persists.

## Dependencies and integration points
The test depends on `utilities/fault_injection_fs.h`, `test_util/testharness.h`, RocksDB filename helpers such as `InfoLogFileName`, `OldInfoLogFileName`, `DescriptorFileName`, and file-writing helpers. It installs the RocksDB stack trace handler in `main()`.

## Risks and edge cases
The concurrent log test deliberately avoids circular-buffer slot reuse to stay TSAN-clean; it does not validate concurrent wraparound. The info-log tests cover only recognized info-log file names, so parser changes in `TryParseFileName()` could shift exclusion behavior. Close forwarding is tested through a layered wrapper that mirrors production ownership but does not exercise every close path such as destructor behavior in the raw target.

## Test signals
Strong direct signals exist for the exact regressions named above. Broader `FaultInjectionTestFS` behavior such as unsynced data loss, async reads, directory recovery, and corruption injection is not covered in this file.
