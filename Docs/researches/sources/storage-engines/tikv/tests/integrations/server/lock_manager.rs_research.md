# sources/storage-engines/tikv/tests/integrations/server/lock_manager.rs

Purpose: tests lock manager deadlock detection, detector leadership, and shared pessimistic lock graph handling.

Important APIs and functions: `deadlock` constructs a two-transaction cycle and validates wait-chain metadata including resource group tags; `kv_shared_pessimistic_lock`, `must_kv_shared_pessimistic_lock`, `force_shared_lock_shrink_only`; `async_pessimistic_lock_resumable`; `build_leader_client`; `must_detect_deadlock`; `deadlock_detector_leader_must_be`; topology helpers for leader transfer, region transfer, split, and merge.

Control flow: `new_cluster_for_deadlock_test` creates a three-peer region, disables PD defaults, sets wait timeout, disables pipelining, transfers leadership, and verifies baseline deadlock detection. Tests mutate leadership, split/merge regions, move regions across stores, and assert detector leadership and detection still work. Shared-lock tests create shared owners, force shrink-only tracking, spawn waiters, and verify deadlock detection, partial-edge cleanup, and waiter updates.

State and persistence: manipulates in-memory wait-for graphs, pessimistic locks, shared lock ownership, region leadership metadata, and raftstore peer membership. Cleanup uses rollback to remove locks and unblock waiting threads.

Dependencies and integration: gRPC `TikvClient`, raftstore topology operations, pessimistic transaction APIs, PD region metadata, and shared-lock behavior.

Risks: concurrency/timing-heavy tests use threads, sleeps, and receive timeouts. Region topology operations can be election-sensitive. Shared-lock cases target subtle stale-edge bugs.

Test signals: detector leadership follows topology changes, deadlock wait chains are accurate, and shared-lock deadlock tracking cleans up and updates waiters correctly.
