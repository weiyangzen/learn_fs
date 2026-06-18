<!-- BEGIN_FILE_RESEARCH: sources/user-network-fs/gcsfuse/tools/gcsfuse-scc-gc/main_test.go -->
# sources/user-network-fs/gcsfuse/tools/gcsfuse-scc-gc/main_test.go

Purpose: Unit tests for the shared chunk cache garbage collector's scan, LRU selection, expiration, and cleanup behavior.

Important APIs, types, and functions: Tests include `TestLRUEviction`, `TestNoEvictionWhenBelowTarget`, `TestBakFileCleanup`, `TestTmpFileCleanup`, `TestOnlyBinFilesProcessed`, `TestMultipleFilesExpiredToReachTarget`, `TestLRUWithIdenticalAtimes`, `TestAtimeFallbackToMtime`, `TestTmpFileAtOneHourBoundary`, `TestEmptyTmpFileList`, and `TestLRUSortingOrderVerification`.

Control flow: Each test creates a temp cache directory and object-like subdirectory structure, writes files with controlled sizes and times via `os.Chtimes`, calls `scanCache`, `findLRUFiles`, `expireFiles`, `removeBakFiles`, or `removeOldTmpFiles`, and asserts filesystem outcomes.

State and persistence behavior: All state is temporary filesystem content under `t.TempDir`. Tests rename files to `.bak`, remove `.bak` and old `.tmp`, and validate recent temp files remain.

Dependencies and integration points: Depends on `testify/assert`/`require` and OS support for file timestamps. It validates behavior expected by external scheduled GC runs.

Risks and test signals: Strong signal for core eviction ordering and cleanup. Gaps include no dry-run CLI test, no `gcsfuse-shared-chunk-cache` subdirectory detection test, no concurrency edge cases, and no empty-directory cleanup depth verification.
<!-- END_FILE_RESEARCH: sources/user-network-fs/gcsfuse/tools/gcsfuse-scc-gc/main_test.go -->
