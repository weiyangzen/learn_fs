# sources/storage-engines/rocksdb/env/mock_env.cc

## Purpose
`mock_env.cc` implements RocksDB's in-memory mock environment: a `MockFileSystem` backed by `MemFile` objects, a `MockEnv` wrapper, and an emulated clock configuration path. It is a test-oriented filesystem/environment that lets RocksDB code exercise file creation, reads, writes, renames, locking, logging, corruption of unsynced bytes, and fake sleeping without touching a real filesystem.

## Important APIs and control flow
The core private type is `MemFile`, which owns file bytes, size, modification time, fsynced byte count, a random generator for corruption, lock-file state, and a manual reference count. `MockSequentialFile`, `MockRandomAccessFile`, `MockRandomRWFile`, and `MockWritableFile` adapt `MemFile` to RocksDB `FS*File` interfaces. `TestMemLogger` writes formatted log lines to a mock writable file.

`MockFileSystem` normalizes paths through `NormalizeMockPath()`, keeps `file_map_` under `mutex_`, and implements the main `FileSystem` operations. Reads and opens check for existence, lock-file misuse, and direct-I/O support. `NewWritableFile()` replaces an existing file, `ReopenWritableFile()` appends to or creates a file, `ReuseWritableFile()` renames then opens, and `LinkFile()` shares a `MemFile` with an extra reference. `RenameFileInternal()` recursively moves children. `CorruptBuffer()` mutates bytes after `fsynced_bytes_`.

## State, persistence, and integration
All file data is process memory; persistence is modeled only by `fsynced_bytes_` so corruption can spare synced prefixes. Modification time comes from the configured `SystemClock`, normally an `EmulatedSystemClock` created by `MockEnv::Create()`. `PrepareOptions()` can adopt the environment clock when the filesystem was built with `SystemClock::Default()`. The file registers option metadata for `supports_direct_io`, while the emulated clock registers `time_elapse_only_sleep` and `mock_sleep`.

`MockEnv` is a `CompositeEnvWrapper` combining a base `Env`, the mock filesystem, and the clock. `NewMemEnv()` preserves older in-memory env behavior by returning `MockEnv::Create(base_env)`.

## Risks and test signals
This mock is intentionally partial. `IsDirectory()` is unsupported, directories are represented as `MemFile`s, and `DeleteDir()` uses relative child names from `GetChildrenInternal()` with `DeleteFileInternal()`, which is a risk for nested directory cleanup semantics. `MockWritableFile::use_direct_io()` currently returns `false && use_direct_io_`, so direct-write reporting is suppressed even when options request it. `NewWritableFile()` creates and inserts the file before returning `NotSupported` for direct writes, leaving observable state on failure. The manual refcounting requires every map insertion/open/link to pair with `Unref()`. Test signals include `mock_env_test`, DB tests using `NewMemEnv`, direct-I/O option tests, file lock behavior, corruption-after-sync behavior, and sync point injection around reads and size checks.
