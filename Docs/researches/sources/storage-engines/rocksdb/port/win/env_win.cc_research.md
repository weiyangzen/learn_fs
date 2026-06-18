# sources/storage-engines/rocksdb/port/win/env_win.cc

Purpose: implements Windows `SystemClock`, `FileSystem`, `Env` I/O helpers, and background-thread integration for RocksDB.

Important APIs/types/functions: `WinClock`, `WinFileSystem::Default`, file creation methods (`NewSequentialFile`, `NewRandomAccessFile`, `NewWritableFile`, `ReopenWritableFile`, `NewRandomRWFile`, `NewMemoryMappedFileBuffer`, `NewDirectory`), file operations (`DeleteFile`, `CreateDir`, `RenameFile`, `LinkFile`, `LockFile`, `GetFreeSpace`, `GetSectorSize`), `WinEnvThreads`, `WinEnv`, and defaults for `FileSystem::Default`/`SystemClock::Default`.

Control flow: `WinClock` prefers `GetSystemTimePreciseAsFileTime` or performance counters. `WinFileSystem` opens handles with Windows share/flag choices matching RocksDB tests and file modes, then wraps them in classes from `io_win.cc`. Directory and metadata methods use Windows attribute and handle APIs. `WinEnvThreads` delegates priority queues to `ThreadPoolImpl` and stores started threads for later joining. `WinEnv` is a `CompositeEnv` over the Windows filesystem and clock.

State and persistence behavior: file methods create, delete, rename, hard-link, lock, preallocate, map, and sync real files through Win32 handles. The clock is stateless after frequency/function-pointer initialization. Thread pools and `threads_to_join_` hold runtime state.

Dependencies and integration points: integrates with RocksDB `Env`, `FileSystem`, `SystemClock`, `ThreadStatusUpdater`, `IOSTATS_TIMER_GUARD`, Windows path macros from `port_win.h`, file wrappers from `io_win.h`, and `WinLogger`.

Risks and test signals: share modes are tuned for RocksDB tests that rename/delete open files. Direct I/O and mmap flags must align with `FileOptions`. `GetChildren` contains a suspicious `BOOL ret = -RX_FindNextFile(...)` idiom but relies on zero/nonzero semantics. Env, logger, WAL, file-lock, fault-injection, and auto-roll logger tests signal regressions.
