# sources/storage-engines/rocksdb/util/filelock_test.cc

Purpose: verifies RocksDB environment file lock behavior, especially same-thread re-lock failure and OS-level lock visibility.

Important APIs/tests: `LockTest` wraps `Env::LockFile()` and `Env::UnlockFile()`. `CheckFileLock()` forks a child on non-Windows systems, attempts an `fcntl(F_SETLK)` write lock, and interprets success/failure according to expected lock state. `LockBySameThread` acquires a lock, verifies contention, attempts duplicate lock, checks error status/message, then unlocks and verifies release.

Control flow: child process opens the lock file and attempts an advisory whole-file write lock. Parent waits for child exit status. Windows path currently returns true as a TODO stub.

State and persistence: uses a per-thread test path and OS file lock state. No durable data beyond the lock file.

Dependencies and integration: includes Env/Status, POSIX `fcntl`, wait headers for BSD variants, coding/string utilities, and test harness.

Risks: fork-based checks are POSIX-specific; Windows does not validate actual lock behavior. Advisory lock semantics differ by filesystem. Same-process file descriptor behavior motivates using a child process.

Test signals: direct signal that Env lock implementation prevents duplicate locks and exposes thread ID in non-Windows error messages.
