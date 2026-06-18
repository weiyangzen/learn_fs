# sources/storage-engines/leveldb/util/env_windows.cc

## Purpose
`env_windows.cc` implements LevelDB's Windows `Env` using Win32 file handles, file mappings, locks, timers, logging, and a background work queue.

## Important APIs, Types, and Functions
Key pieces include `ScopedHandle`, `Limiter`, `WindowsSequentialFile`, `WindowsRandomAccessFile`, `WindowsMmapReadableFile`, `WindowsWritableFile`, `WindowsFileLock`, `WindowsEnv`, `SingletonEnv`, and `EnvWindowsTestHelper::SetReadOnlyMMapLimit`.

## Control Flow
File creation uses `CreateFileA` with appropriate access/share modes. Random reads prefer memory mapping while the mmap limiter permits it, otherwise use overlapped `ReadFile`. Writable files buffer 64 KiB and flush with `FlushFileBuffers`; parent directory sync is omitted because Windows updates metadata through file creation. Rename first tries `MoveFileA`, then `ReplaceFileA` for existing targets. `Schedule` lazily starts one detached background thread and drains a FIFO work queue.

## State, Persistence, and Integration
State includes RAII handles, mmap limiter, background queue, and singleton env storage. Persistent effects are real filesystem files, renames, locks, and logs. It integrates with generic env tests and Windows-specific open-on-read tests.

## Risks and Test Signals
Windows-specific risks include share modes, append handle semantics, partial writes not being retried, path encoding limited to ANSI APIs, and mmap fallback on empty or failed mappings. Tests cover mmap limit fallback; generic env tests cover file IO and scheduling.
