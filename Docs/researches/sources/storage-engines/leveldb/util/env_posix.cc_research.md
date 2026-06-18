# sources/storage-engines/leveldb/util/env_posix.cc

## Purpose
`env_posix.cc` implements LevelDB's POSIX `Env` using file descriptors, mmap, filesystem calls, locks, logging, timers, and a background work queue.

## Important APIs, Types, and Functions
Key classes are `Limiter`, `PosixSequentialFile`, `PosixRandomAccessFile`, `PosixMmapReadableFile`, `PosixWritableFile`, `PosixFileLock`, `PosixLockTable`, `PosixEnv`, and `SingletonEnv`. Test hooks are `EnvPosixTestHelper::SetReadOnlyFDLimit` and `SetReadOnlyMMapLimit`.

## Control Flow
Sequential reads use `read` with EINTR retry. Random reads prefer mmap while the mmap limiter has capacity, then permanent file descriptors while the fd limiter has capacity, then open-on-read. Writable files buffer 64 KiB, retry interrupted writes, sync manifest parent directories before syncing the manifest file, and use `fdatasync`/`fsync`/`F_FULLFSYNC` as available. Locks combine process-local `PosixLockTable` with `fcntl` whole-file locks. `Schedule` lazily starts one detached background thread that drains a FIFO queue.

## State, Persistence, and Integration
State includes global resource limits, limiter counters, open fds/mmap regions, process lock table, background queue, and singleton env storage whose destructor intentionally never runs. It integrates with all DB file IO, table reads, logs/manifests, tests, and POSIX logger.

## Risks and Test Signals
Empty mmap files, fd exhaustion, directory sync semantics, process-local duplicate locks, EINTR handling, and close-on-exec behavior are key risks. POSIX env tests cover open-on-read fallback and close-on-exec for sequential/random/writable/appendable/lock/logger handles; generic env tests cover read/write, scheduling, threads, missing files, rewrite, and append.
