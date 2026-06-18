<!-- BEGIN_FILE_RESEARCH: sources/object-store/rustfs/crates/lock/src/fast_lock/tests.rs -->
# sources/object-store/rustfs/crates/lock/src/fast_lock/tests.rs

Purpose: `fast_lock/tests.rs` is the integration-style unit test module for the fast lock facade. It validates externally visible manager, guard, key, timeout, and contention behavior using Tokio tests.

Important APIs/types/functions: the test helper `create_test_manager` builds a `FastObjectLockManager` with four shards and shorter defaults. Tests exercise `acquire_write_lock`, `acquire_read_lock`, `acquire_lock` with custom `ObjectLockRequest`, `FastLockGuard::release`, automatic `Drop`, `ObjectKey::with_version`, and `LockResult::Timeout`.

Control flow: the tests acquire guards through the manager, assert guard fields, release explicitly or by drop, and then attempt conflicting/follow-up acquisitions. Concurrency tests spawn multiple reader or writer tasks with shared `Arc<FastObjectLockManager>`. Timeout tests create contended requests with short acquire timeouts to make failures deterministic.

State and persistence behavior: test state is in-memory and per manager. Versioned keys are treated as independent `ObjectKey` values, so latest and version-specific locks can coexist. Drop tests rely on RAII release rather than background cleanup.

Dependencies and integration points: these tests cover the interaction of `manager.rs`, `shard.rs`, `state.rs`, `guard.rs`, and `types.rs`. They indirectly validate `LockConfig` defaults and `LockPriority` plumbing, but not `GlobalLockManager` env selection.

Risks surfaced by tests: same-owner exclusive acquisition is intentionally not reentrant and should time out; high-priority write locks still cannot bypass an existing exclusive lock; write locks exclude readers and other writers; read locks exclude writers but allow multiple readers; a released guard no longer reports lock info. These are contract signals for downstream namespace/object-store code.

Test gaps: the suite is good for basic behavior but does not include long-running stress, randomized cancellation, reader-count cap, cleanup/pool recycling, metrics accuracy, or disabled-lock mode. It also does not assert background cleanup shutdown behavior. Namespace tests provide broader distributed coverage.
<!-- END_FILE_RESEARCH: sources/object-store/rustfs/crates/lock/src/fast_lock/tests.rs -->
