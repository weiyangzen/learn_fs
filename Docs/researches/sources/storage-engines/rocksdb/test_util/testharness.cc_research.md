# sources/storage-engines/rocksdb/test_util/testharness.cc

Purpose: implements common gtest harness helpers for RocksDB tests: process/thread-specific paths, random seed selection, memory gating, status assertions, regex assertions, and debug sync-point cleanup.

Important APIs/control flow: a debug-only `SyncPointCleanupListener` is statically registered with gtest and clears sync-point processing, callbacks, traces, and dependencies after every test. `GetPidStr()` abstracts process ID across Windows/POSIX. `TmpDir()`, `PerThreadDBPath()`, `RandomSeed()`, and `HasBigMem()` provide environment-sensitive test setup. `AssertStatus()` and `AssertMatchesRegex()` produce gtest assertion results. `TestRegex` wraps `std::regex` behind a shared implementation.

State behavior: static listener registration mutates gtest global listener state. `RandomSeed()` reads `TEST_RANDOM_SEED`, and `HasBigMem()` reads `ROCKSDB_BIGMEM_TESTS` and physical memory via `sysconf` when available.

Dependencies/integration: integrates with gtest, Env test directories, stack trace/test utilities, and sync-point debug infrastructure.

Risks and test signals: static listener ordering matters, but it prevents stale callbacks from sharded test processes. `PerThreadDBPath()` hashes thread IDs, so it is unique enough for tests but not a persistent naming scheme. Tests should cover regex assertion messages, invalid seeds defaulting to 301, big-memory gating, and sync-point cleanup between tests.
