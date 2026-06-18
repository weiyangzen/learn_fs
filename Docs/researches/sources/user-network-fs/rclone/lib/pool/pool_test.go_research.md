# sources/user-network-fs/rclone/lib/pool/pool_test.go

<!-- BEGIN_FILE_RESEARCH: sources/user-network-fs/rclone/lib/pool/pool_test.go -->
## sources/user-network-fs/rclone/lib/pool/pool_test.go

Purpose: validates `Pool` allocation, reuse, flush aging, mmap/non-mmap modes, failure retry behavior, and global memory limiting.

Important APIs and control flow: `testGetPut` checks `InUse`, `InPool`, and `Alloced` through several `Get`, `GetN`, `Put`, and `PutN` sequences, including pointer reuse order and overflow freeing. `makeUnreliable` replaces allocator/free functions to intermittently fail so retry/error logging paths are exercised. `testFlusher` uses short timers and manual `flushAged` calls to verify `minFill`-based eviction. `TestPoolMaxBufferMemory` resets package singleton state, sets `MaxBufferMemory`, then runs concurrent `Get`/`GetN` callers and asserts active buffers never exceed the configured limit.

State, dependencies, and integration: the test mutates global fs config and package globals (`totalMemoryInit`, `totalMemory`) and restores them afterward. It depends on `testy.SkipUnreliable` for flaky allocator/free simulation on some platforms.

Risks and test signals: these tests are strong signals for core pool invariants and resource accounting. They do not assert log output or exact retry timing. Because they manipulate package-level globals, they assume serial test execution around global memory tests.
<!-- END_FILE_RESEARCH: sources/user-network-fs/rclone/lib/pool/pool_test.go -->
