# sources/storage-engines/rocksdb/file/file_util.h

## Purpose

`file_util.h` is a shared file-operation helper interface for RocksDB internals. It declares copy/create/delete/checksum helpers and small option-conversion utilities that bridge public `ReadOptions`/`WriteOptions` to lower-level `IOOptions`. It also exposes a test-only destructive directory cleanup helper and a filesystem feature probe.

## Important APIs, Types, and Functions

- `CopyFile(...)` has two overload families: one copies from a source path into an existing `WritableFileWriter`, and another opens/writes a destination path with destination `Temperature`. Both accept source/destination temperature hints, target size, fsync behavior, `IOTracer`, read/write `IOOptions`, and a maximum read buffer size.
- `CreateFile(...)` writes a full string to a destination file and optionally fsyncs.
- `DeleteDBFile(...)` and `DeleteUnaccountedDBFile(...)` centralize DB-file deletion while respecting `ImmutableDBOptions`, foreground/background deletion policy, directory sync paths, and optional slow-deletion trash buckets.
- `GenerateOneFileChecksum(...)` computes one file checksum using a `FileChecksumGenFactory`, requested checksum function name, readahead size, mmap policy, tracing, rate limiting, statistics, clock, read options, and file options.
- `PrepareIOFromReadOptions(...)` maps `ReadOptions` request id, deadline, `io_timeout`, rate limiter priority, and IO activity onto `IOOptions` and `IODebugContext`.
- `PrepareIOFromWriteOptions(...)` maps write rate limiter priority and IO activity.
- `DestroyDir(...)` is explicitly destructive and intended only for tests.
- `CheckFSFeatureSupport(...)` queries `FileSystem::SupportedOps` and checks the bit for a `FSSupportedOps` enum value.

## Control Flow and State

Most declarations defer implementation to corresponding `.cc` files. The inline path in `PrepareIOFromReadOptions` first propagates `request_id` into debug context if unset, then computes remaining deadline using `SystemClock::NowMicros()`. If the deadline has already passed, it returns `IOStatus::TimedOut`; otherwise it uses the tighter timeout between absolute deadline remainder and relative `io_timeout`. The function finally copies priority and activity fields. `PrepareIOFromWriteOptions` is simpler and has no failure path today.

The helpers do not own persistent state. They pass through filesystem handles, tracing, stats, and rate limiters. Persistence behavior is delegated to implementations: copy/create operations can fsync based on `use_fsync`; deletion helpers coordinate with `SstFileManager`/delete scheduler expectations; checksum generation performs read-only scans.

## Dependencies and Integration Points

This header depends on RocksDB file naming, DB options, `Env`, `FileSystem`, SST writer options, statistics, status, clocks, and IO tracing. It is included by `filename.cc` for `PrepareIOFromWriteOptions` and file writing; `random_access_file_reader.cc` for read option preparation; tests for `DestroyDir`; and readahead code for debug-only sector-alignment assertions.

## Risks and Edge Cases

- Passing a null or stale `SystemClock` into `PrepareIOFromReadOptions` would break deadline handling; callers generally use DB/system clocks.
- A deadline equal to or earlier than `NowMicros()` returns timeout intentionally to avoid passing zero timeout, which would mean no timeout.
- Deletion helpers rely on callers correctly classifying tracked versus unaccounted SST/blob files; using the wrong helper can skew size/trash accounting.
- `CheckFSFeatureSupport` assumes the enum value maps to a supported-ops bit position.

## Test Signals

`DestroyDir` is used in local tests such as `random_access_file_reader_test.cc` and `prefetch_test.cc` cleanup. `PrepareIOFromReadOptions` is indirectly exercised by random-access reads and tests that pass `IOOptions`/`ReadOptions` through reader paths. Deletion and checksum declarations need implementation-level coverage outside this header.
