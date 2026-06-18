# sources/storage-engines/tikv/tests/failpoints/cases/test_kv_service.rs

## Purpose
This file tests KV service failpoint behavior around snapshot errors, gRPC responsiveness, stale reads, transaction status cache correctness, in-memory pessimistic locks, and duplicate-key diagnostics.

## Important APIs, Types, and Functions
- Test cases are parameterized across raftstore v1 and v2 where behavior is shared via `test_case`.
- `must_new_cluster_and_kv_client`, `must_new_cluster_mul`, `new_server_cluster`, and `configure_for_lease_read` build service-facing clusters and clients.
- KV RPC types include `BatchGetRequest`, `ScanRequest`, `GetRequest`, `PrewriteRequest`, `CommitRequest`, `ScanLockRequest`, and `TikvClient`.
- `must_kv_prewrite`, `must_kv_commit`, `must_kv_pessimistic_lock`, `try_kv_prewrite_with`, and `must_kv_have_locks` drive transactional storage behavior.

## Control Flow
The first two tests inject `raftkv_async_snapshot_err` and assert batch-get and scan return the compatibility error both per item and at top-level response. `test_snapshot_not_block_grpc` pauses snapshot acquisition after one successful write and proves a second RPC does not trip keepalive timeout. `test_undetermined_write_err` injects `applied_cb_return_undetermined_err`, expects a cancelled RPC failure, and then verifies the cluster panic is still captured on drop. Stale-read and status-cache tests build one-node clusters, create locks or write errors, then verify fallback and cache-hit/miss behavior. The scan-lock test stages in-memory pessimistic locks, starts a leader transfer failpoint after proposing locks, then confirms scans do not return duplicate locks from memory and storage. The ignored duplicate-key test exercises scheduler duplicate-key checks.

## State and Persistence Behavior
The tests distinguish memory locks from persisted lock CF entries, ensuring scan-lock merges both sources without duplicates. Transaction status cache is allowed to cache successful writes but must not be updated by region-error write failures. Stale read on a local leader should fall back to a safe read path when a lock at a later timestamp exists. The gRPC test targets runtime scheduling state rather than RocksDB persistence.

## Dependencies and Integration Points
This suite integrates storage RPC handlers with raftstore snapshots, lease-read configuration, pessimistic lock memory tables, lock CF reads through `engine_traits::Peekable`, and TiKV gRPC clients. Failpoints such as `after-snapshot`, `raftkv_early_error_report`, `finish_proposing_transfer_cmd_after_proposing_locks`, and `scheduler_dup_key_check` isolate service/raftstore boundaries.

## Risks and Test Signals
Risks include returning errors in only one legacy response field, gRPC keepalive watchdog false positives, stale reads incorrectly surfacing locks, transaction status cache pollution after failed writes, and duplicate lock reporting during leader transfer. Test signals are explicit response fields, CF lock absence/presence checks, panic failpoints for impossible cache paths, and lock-count assertions.
