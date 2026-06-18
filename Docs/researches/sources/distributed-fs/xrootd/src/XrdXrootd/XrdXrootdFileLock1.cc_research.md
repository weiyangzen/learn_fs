# sources/distributed-fs/xrootd/src/XrdXrootd/XrdXrootdFileLock1.cc

Purpose: implements the default single-process, per-host file lock manager using an in-memory hash table keyed by path. It tracks reader and writer counts and enforces simple read/write exclusion unless forced.

Important APIs and functions: `Lock()` looks up path state in global `XrdXrootdLockTable`. A read lock conflicts with existing writers unless `force` is true; a write lock conflicts with any reader or writer unless forced. It increments counts or creates a new `XrdXrootdFileLockInfo`. `numLocks()` returns current counts. `Unlock()` decrements the relevant count, rejects missing or underflowed locks, and deletes the hash entry when both counts reach zero.

Control flow and state: all hash access is protected by static `LTMutex`, wrapped by a small RAII helper `XrdXrootdLockFileLock`. State persists for the process lifetime in `XrdXrootdLockTable`.

Dependencies and integration: depends on `XrdOucHash`, `XrdSysMutex`, and the abstract `XrdXrootdFileLock` interface. Instantiated during protocol configuration and used by file open/close paths.

Risks and test signals: this manager is not distributed and only protects one server process. Tests should cover multiple readers, writer conflicts, forced locks, unlock without lock, count deletion at zero, and concurrent lock/unlock calls.
