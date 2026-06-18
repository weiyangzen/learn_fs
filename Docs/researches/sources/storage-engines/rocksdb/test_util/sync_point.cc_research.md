# sources/storage-engines/rocksdb/test_util/sync_point.cc

Purpose: provides the public `SyncPoint` singleton wrappers, direct-I/O mocking hooks, global kill-point exclusion storage, and debug-only testable assertion state.

Important APIs/control flow: in non-release builds `SyncPoint::GetInstance()` returns a static singleton whose methods delegate to `SyncPoint::Data`: loading dependencies/markers, registering callbacks, clearing state, enabling/disabling, and processing points. `SetupSyncPointsToMockDirectIO()` registers callbacks that clear `O_DIRECT` from writable, random-access, and sequential file creation flags on supported platforms.

State behavior: owns the singleton `Data` through a raw pointer and deletes it in the destructor. `rocksdb_kill_exclude_prefixes` is a global vector outside the RocksDB namespace. `g_throw_on_testable_assertion_failure` is a debug-only atomic counter used by `testable_assert`.

Dependencies/integration: depends on `sync_point_impl.h`, platform `fcntl.h`, and RocksDB tests that compile `TEST_SYNC_POINT` macros. Direct-I/O mocking integrates with Env file creation sync points.

Risks and test signals: all substantive behavior disappears under `NDEBUG` except direct-I/O setup's outer symbol. Global sync-point state can leak between tests if not cleared. Tests should validate callback delegation, cleanup behavior, direct-I/O flag mutation, and release-build no-op compilation.
