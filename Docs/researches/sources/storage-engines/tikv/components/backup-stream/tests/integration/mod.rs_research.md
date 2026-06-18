# sources/storage-engines/tikv/components/backup-stream/tests/integration/mod.rs

## Purpose
This file is the non-failpoint backup-stream integration suite. It validates normal and adverse cluster behavior for PiTR/log backup, including region splits, region metadata boundaries, large transaction ordering around initial scans, leader loss, async commit, checkpoint querying, upload cancellation, pessimistic locks, flush subscriptions, follower resolution, network partition safety, dynamic config changes, force flush, and monotonic flush timestamps across PD TSO failures.

## Important APIs, Types, And Functions
The module uses `SuiteBuilder`, `run_async_test`, record/split key helpers, backup-stream `Task`, `RegionCheckpointOperation`, `RegionSet`, `GetCheckpointResult`, `TaskSelector`, `utils::parse_backupmeta_filename`, PD client failure hooks, grpc flush subscription streams, and `WalkDir` metadata inspection. Helper functions `collect_all_current`, `collect_current`, and `collect_meta_filenames` support async stream assertions and backupmeta filename validation.

## Control Flow
Tests construct simulated clusters, optionally split regions or alter leaders, register stream backup tasks, perform transactional writes, force flushes, and verify produced files/checkpoints. Subscription tests collect flush events until expected counts or timeout. Network partition tests isolate a leader, force leader expiration, write unresolved data, flush, and assert emitted checkpoints do not pass the locked timestamp. TSO failure tests repeatedly invoke `flush_now`, inspect success/failure results, and compare generated backupmeta names.

## State And Persistence Behavior
The suite validates persisted backup data files and `v1/backupmeta` contents. `region_boundaries` parses metadata and checks region start/end keys and epochs for data files. `monotonic_flush_ts_across_pd_failure` ensures no metadata files are produced before any successful TSO allocation, then ensures later flushes continue with monotonic local flush timestamps even if PD TSO fails again. `flush_status_is_cleared_when_tso_allocation_fails` verifies in-memory flushing flags are reset and later flushes recover.

## Dependencies And Integration Points
The tests integrate backup-stream endpoints, raftstore region state, PD TSO and region APIs, gRPC `LogBackupClient`, TiKV transactional KV APIs, flush subscription protocol, backup-stream metadata naming utilities, and the local backup file reader/checker in the shared suite. They also use `IsolationFilterFactory` to simulate network partitions.

## Risks And Edge Cases
Several assertions are bounded by timeouts or sleeps and can be sensitive to slow CI. The checkpoint tests rely on the shared suite's global checkpoint approximation, which explicitly does not check full region consistency. Network partition safety hinges on the simulated isolation filter and unresolved lock pattern. The metadata monotonicity test assumes exactly two successful metadata files for the chosen workload.

## Test Signals
The integration suite provides strong behavioral coverage for split handling, region epoch metadata, split transactions with more than 1024 short-value mutations, leader failure continuity, async commit checkpoint blocking/unblocking, pessimistic lock nonblocking behavior, flush subscription event ranges, follower checkpoint resolution, network partition safety, online config semaphore resizing, and PD TSO failure recovery.
