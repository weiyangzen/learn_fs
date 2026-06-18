# sources/storage-engines/tikv/components/raftstore-v2/tests/failpoints/test_bootstrap.rs

## Purpose
This file tests raftstore-v2 bootstrap idempotence and recovery when failpoints abort startup at key points between store bootstrap, prepare-bootstrap-region persistence, and cluster bootstrap completion.

## Important APIs, Types, and Functions
- `test_bootstrap_half_way_failure()` constructs a `test_pd` server/client, temp engines, and a closure that calls `Bootstrap::bootstrap_store()` followed by `bootstrap_first_region()`.
- Failpoints `node_after_bootstrap_store`, `node_after_prepare_bootstrap_cluster`, and `node_after_bootstrap_cluster` inject aborts at successive bootstrap stages.
- It reads `get_store_ident()` and `get_prepare_bootstrap_region()` from the raft engine to verify persisted metadata.

## Control Flow
The test first aborts after store bootstrap and expects no prepared bootstrap region but a nonzero store id. It then removes that failpoint, aborts after prepare-bootstrap-cluster, and checks that a prepared region exists. It aborts after bootstrap-cluster and still expects prepared metadata. Finally it runs bootstrap without failpoints, expecting recovery to finish and clear the prepared region, then verifies a second bootstrap is a no-op.

## State and Persistence Behavior
The test centers on raft-engine bootstrap metadata: store ident and prepared bootstrap region. It validates that partially persisted bootstrap state is either safely absent or resumable, and that successful completion clears the prepare marker.

## Dependencies and Integration Points
It integrates `raftstore_v2::Bootstrap`, `test_pd`, `engine_test::new_temp_engine`, raft-engine read-only bootstrap metadata APIs, and `kvproto::metapb::Store`.

## Risks and Edge Cases
- Bootstrap must be idempotent across process crashes after any single persisted marker.
- Prepared bootstrap-region metadata must not be left behind after successful cluster bootstrap.
- A store id persisted before first-region bootstrap must be reused rather than reallocated.

## Test Signals
The test checks error strings include failpoint names, metadata presence/absence at each phase, final successful bootstrap result, and second-run no-op behavior.
