# sources/storage-engines/tikv/tests/failpoints/cases/test_read_execution_tracker.rs

## Purpose
This file verifies that execution detail metrics distinguish lease reads from read-index reads for get, batch get, and coprocessor requests.

## Important APIs, Types, and Functions
- `test_read_execution_tracking` is parameterized across raftstore v1 and v2 cluster/client constructors.
- It uses `ScanDetailV2` fields: `read_index_propose_wait_nanos`, `read_index_confirm_wait_nanos`, and `read_pool_schedule_wait_nanos`.
- KV helpers `kv_read`, `kv_batch_read`, `must_kv_prewrite`, `must_kv_commit`, and coprocessor `DagSelect` drive three read surfaces.
- Failpoints `perform_read_local` and `perform_read_index` force the intended read path.

## Control Flow
The test configures lease reads with a very small pre-renew duration, writes and commits two keys, defines a checker that expects no read-index waits for lease reads, forces local read, and validates get, batch get, and coprocessor responses. It then removes the local-read failpoint, defines a checker expecting positive read-index propose/confirm waits, forces read-index twice per request path, and validates the same three read surfaces.

## State and Persistence Behavior
The persisted state is simple committed MVCC data for two keys and a ProductTable row. The primary state under test is response execution detail accounting for scheduling and read-index phases.

## Dependencies and Integration Points
The test integrates transactional KV writes, lease-read configuration, read pool scheduling, read-index handling, coprocessor DAG execution, and response `exec_details_v2` metrics.

## Risks and Test Signals
Risks include metrics missing read-index waits, incorrectly charging lease reads for read-index waits, or failing to populate read-pool scheduling wait. Signals are strict zero/non-zero assertions over `ScanDetailV2` for all three read request types.
