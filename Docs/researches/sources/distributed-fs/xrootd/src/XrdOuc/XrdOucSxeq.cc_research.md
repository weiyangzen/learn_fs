# sources/distributed-fs/xrootd/src/XrdOuc/XrdOucSxeq.cc

Purpose: implements file-based serialization locks using `fcntl()` record locks, with optional shared mode, non-blocking mode, and unlink-on-destruction for exclusive lock files.

Important APIs, types, and functions: constructors open or build lock-file paths; `Serialize()` acquires read or write locks; `Release()` unlocks; static `Serialize(int, int)` and `Release(int)` operate on external descriptors; destructor optionally unlinks and closes.

Control flow: construction opens the lock file with user-write/group/world-read permissions and may immediately call `Serialize()`. `Serialize()` builds an `FLOCK_t`, chooses `F_SETLK` or `F_SETLKW`, retries on `EINTR`, sets `lokUL` if an exclusive unlink-on-release lock was requested, and records `lokRC`. `Release()` unlocks and disables pending unlink.

State and persistence: object state is the lock filename, descriptor, unlink flag, and last error. Lock state is kernel-managed against the open file description. The lock file may persist unless `Unlink` is used and the object is destroyed while locked.

Dependencies and integration points: depends on POSIX `open`, `fcntl`, `close`, `unlink`, `sys/stat`, `MAXPATHLEN`, and `XrdSysPlatform.hh` for `FLOCK_t`. It integrates with process-level singleton/critical-section code.

Risks and test signals: the path-concatenating constructor uses `strcpy()` into a fixed `MAXPATHLEN+1` buffer without length checks. `Release()` returns `0` on unopened object while static `Release()` returns `EBADF`, so callers must distinguish APIs. Tests should cover shared/exclusive contention between processes, non-blocking failure, EINTR retry, unlink behavior, long paths, and destructor cleanup.
