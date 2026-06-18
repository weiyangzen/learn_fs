# sources/object-store/rustfs/crates/e2e_test/src/reliant/lock.rs

## sources/object-store/rustfs/crates/e2e_test/src/reliant/lock.rs

Purpose: local async tests for distributed namespace locking over gRPC-backed lock clients. They verify quorum behavior, health reporting, batch lock operations, lock-ID preservation, and split read/write quorum semantics.

Important APIs and types: `test_resource` returns a stable `ObjectKey`. `FailingClient` implements `rustfs_lock::LockClient` by failing acquisitions and reporting offline. `failing_grpc_client` wraps `FailingClient` behind `spawn_lock_server` and `GrpcLockClient`. Tests exercise `GlobalLockManager`, `LocalClient::with_manager`, `NamespaceLock::with_clients`, `NamespaceLock::with_clients_and_quorum`, lock guards, `LockRequest`, `LockType`, and gRPC helper modules.

Control flow: `test_distributed_lock_4_nodes_grpc` starts four in-memory lock managers behind four gRPC servers, acquires a write lock with owner A, verifies owner B cannot get the lock, releases A, verifies B can acquire, and checks health shows four connected nodes. `test_distributed_lock_2_nodes_grpc_read_survives_failed_node` combines one healthy and one failing gRPC node with quorum two, expecting read lock success but write lock failure. `test_grpc_lock_client_batch_acquire_and_release` validates batch acquisition and release for two resources. `test_grpc_lock_client_uses_request_lock_id_and_reports_missing_unlock` ensures the server preserves request lock IDs and reports a second release as missing. `test_distributed_lock_4_nodes_grpc_read_write_quorum_split_with_two_failed_nodes` expects read success and write failure with two healthy/two failed nodes.

State and persistence: lock state is in-memory inside `GlobalLockManager` instances. gRPC servers are bound to ephemeral ports and aborted at test end. Guards own release state and are dropped or explicitly released.

Dependencies and integration points: `rustfs_lock`, local and gRPC lock client/server test shims, Tokio tasks/time, async trait implementation, and in-memory lock managers.

Risks: tests use fixed sleeps for server startup. Aborting server handles is abrupt. The quorum expectations encode read/write quorum policy details that may change with lock algorithm changes. `FailingClient` only simulates acquisition failure and offline health in a narrow way.

Test signals: strong unit/e2e hybrid signal for distributed lock quorum, contention, release, batch RPC shape, request lock ID semantics, and degraded-node behavior.
<!-- END_FILE_RESEARCH: sources/object-store/rustfs/crates/e2e_test/src/reliant/lock.rs -->
