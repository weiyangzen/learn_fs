# sources/storage-engines/rocksdb/env/mock_env.h

## Purpose
`mock_env.h` declares the public test-facing in-memory filesystem and environment types used by RocksDB tests. It exposes `MockFileSystem`, which implements the `FileSystem` interface, and `MockEnv`, which wraps a base `Env` with that filesystem and an emulated/system clock.

## Important APIs and types
`MockFileSystem` overrides file creation/opening APIs for sequential, random-access, random-RW, writable, reopened writable, reused writable, directory, logger, lock, and sync operations. It also exposes filesystem metadata operations such as `FileExists`, `GetChildren`, `DeleteFile`, `Truncate`, `CreateDir`, `DeleteDir`, `GetFileSize`, `GetFileModificationTime`, `RenameFile`, `LinkFile`, `GetTestDirectory`, and `GetAbsolutePath`. `CorruptBuffer()` is a test hook for corrupting unsynced in-memory bytes. `PrepareOptions()` lets config parsing rebind the clock.

Private state is a mutex-protected `std::map<std::string, MemFile*>`, a `SystemClock` shared pointer/raw pointer pair, and a `supports_direct_io_` flag. Helper methods perform path normalization, internal rename/delete, and child discovery.

`MockEnv` derives from `CompositeEnvWrapper`, provides two static `Create()` factories, reports class name `MockEnv`, and forwards `CorruptBuffer()` to the underlying `MockFileSystem`.

## State, dependencies, and integration
The header depends on RocksDB's `FileSystem`, `Env`, `Status`, `SystemClock`, `CompositeEnvWrapper`, and port mutex abstractions. It is not a general production filesystem contract; it is a test utility that supplies enough `FileSystem` behavior for DB tests and examples of environment composition.

## Risks and test signals
The API surface is broad while the implementation is partial. Callers that assume all `FileSystem` methods are production-complete can hit `NotSupported`, especially for directory classification. Because the header exposes `MockFileSystem` directly, tests may depend on implementation quirks such as normalized absolute paths, in-memory lock files, and direct-I/O toggles. Test signals are successful compilation of env tests, option parsing for registered mock options, and behavioral tests around file corruption, fake sleeping, locks, children, renames, and unsupported calls.
