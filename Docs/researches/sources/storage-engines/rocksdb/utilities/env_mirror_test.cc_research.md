# sources/storage-engines/rocksdb/utilities/env_mirror_test.cc

## Purpose
This file tests `EnvMirror` using two `MockEnv` backends. It verifies that mirrored operations affect both backends and that reads through the mirror return expected data.

## Important APIs, Types, and Functions
`EnvMirrorTest` owns `Env::Default()`, two `MockEnv` instances, and an `EnvMirror`. Tests are `Basics`, `ReadWrite`, `Locks`, `Misc`, and `LargeWrite`. The file-level `main` installs the stack trace handler and runs GoogleTest.

## Control Flow
`Basics` creates directories/files, checks existence and children on the mirror and each backend, writes data, renames, attempts missing-file opens/deletes, and deletes the directory. `ReadWrite` writes `hello world`, reads sequentially with skip and EOF behavior, then performs random reads and an out-of-range read. `Locks` verifies lock/unlock success. `Misc` checks test directory discovery and writable-file sync/flush/close. `LargeWrite` writes a 300 KiB deterministic byte string and reads it back sequentially in chunks.

## State and Persistence Behavior
All persistent test state lives inside two `MockEnv` instances. The tests ensure mirrored writes are visible in both, and fixture teardown deletes the mirror and backends.

## Dependencies and Integration Points
The test depends on `rocksdb/utilities/env_mirror.h`, `env/mock_env.h`, and RocksDB's test harness. It indirectly validates the mirror wrappers in `env_mirror.cc`.

## Risks and Edge Cases
The tests do not intentionally create divergent backends, so assert-based mismatch detection is not directly exercised. Positioned append, truncate, allocate, range sync, invalidate cache, and unique ID paths are not covered. Because `MockEnv` behavior is idealized, platform-specific filesystem behavior is not tested.

## Test Signals
Passing tests show basic mirroring semantics, backend parity for metadata operations, correct sequential/random reads, and ability to handle large sequential data without corruption.
