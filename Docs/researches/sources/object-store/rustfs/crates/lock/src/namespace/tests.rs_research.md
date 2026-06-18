<!-- BEGIN_FILE_RESEARCH: sources/object-store/rustfs/crates/lock/src/namespace/tests.rs -->
# sources/object-store/rustfs/crates/lock/src/namespace/tests.rs

Purpose: `namespace/tests.rs` is the primary behavioral test suite for the namespace facade and distributed quorum semantics. It validates local wrappers and simulated multi-node distributed locking with custom clients.

Important APIs/types/functions: helper client types include `FailingClient`, `FailureResponseClient`, `DelayedClient`, `FlakyAcquireClient`, and `FlakyReleaseClient`. Helpers `create_test_object_key` and `wait_until_all_managers_can_write` build keys and verify cleanup across simulated nodes. Tests exercise `NamespaceLock`, `NamespaceLockGuard`, `NamespaceLockWrapper`, `LocalClient`, `GlobalLockManager`, `LockClient` batch defaults, and distributed read/write operations.

Control flow: local tests instantiate managers and assert local guard variants, release behavior, wrapper owner/resource usage, health, and stats. Distributed tests build multiple `LocalClient`s backed by independent managers, acquire quorum locks, assert contention failures, release guards, and probe every manager for cleanup. Failure tests inject offline clients, RPC-like failure responses, delayed clients, transient acquisition failures, and release failures to verify retry/rollback/early-return behavior.

State and persistence behavior: all simulated nodes are in-memory `GlobalLockManager` instances. Distributed guards are expected to release all successful node locks, including rollback after quorum failure and cleanup of late successes from slow clients. Tests deliberately drop a distributed guard after its runtime is gone to ensure drop does not panic and cleanup can later complete.

Dependencies and integration points: covers the interaction of namespace facade, distributed lock implementation, client trait, local client, global manager, and fast lock internals. It is a strong integration signal for object-store code that maps quorum failures into storage errors.

Risks captured: two-node read locks can succeed with one healthy node while writes fail with one offline node; remote RPC failures should be hard quorum failures rather than contention timeouts; ordinary contention should exhaust timeout and not masquerade as quorum loss; failed quorum must roll back successful nodes; late successes from slow clients must be cleaned up after early success or early failure; release false values should be retried.

Test gaps: these tests are comprehensive for quorum behavior but use deterministic simulated clients, not real network RPC. They do not test environment-disabled global managers, namespace collision in local mode, metrics exposure, or high-volume concurrent distributed operations beyond selected scenarios.
<!-- END_FILE_RESEARCH: sources/object-store/rustfs/crates/lock/src/namespace/tests.rs -->
