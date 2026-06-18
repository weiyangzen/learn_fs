# sources/storage-engines/tikv/components/backup-stream/tests/failpoints/mod.rs

## Purpose
This file is the failpoint-backed backup-stream integration test module. It uses a custom failpoint test runner and the shared `suite.rs` harness to verify recovery and correctness under injected failures in task registration, observation startup, initial scanning, region refresh, retry abort, flush/resolve races, encryption, fatal error handling, and force-flush concurrency.

## Important APIs, Types, And Functions
The module reexports the shared suite and defines tests inside `mod all`. Tests use `SuiteBuilder`, `Suite`, `run_async_test`, key constructors, `mutation`, metadata clients/stores, `Task`, `RegionCheckpointOperation`, `RegionSet`, `TaskSelector`, `PauseStatus`, failpoint configuration APIs, and walkdir inspection. Notable scenarios include `failed_register_task`, `basic`, `frequent_initial_scan`, `initial_region_scan_does_not_deadlock_when_operator_queue_fills`, `region_failure`, `initial_scan_failure`, `failed_during_refresh_region`, `test_retry_abort`, `failure_and_split`, `memory_quota`, `resolve_during_flushing`, `commit_during_flushing`, `encryption`, `failed_to_get_task_when_pausing`, `fatal_error`, and `pending_flush_when_force_flush`.

## Control Flow
Each test builds a simulated TiKV cluster, registers a backup stream task through metadata, injects failpoints at a specific backup-stream stage, performs writes/splits/leader changes/flushes, and then validates either flushed data or control-plane state. The tests generally follow the pattern: prepare data, register task, trigger failure or race, wait for suite synchronization/flush completion, then assert recovered output or uploaded metadata. Retry-oriented tests remove pause/error metadata and verify that routers recreate task handlers after recovery.

## State And Persistence Behavior
The tests exercise both metadata state and file state. Metadata assertions inspect task last errors, pause status JSON/protobuf payloads, safepoints, global/region checkpoints, and task handler presence in routers. File assertions inspect flushed backup data under temp local storage and, for encryption, temporary files under the backup-stream temp directory. Several tests explicitly verify that checkpoints do not advance past unsafe timestamps during races and that fatal errors pause tasks and install GC safepoints.

## Dependencies And Integration Points
This module depends on the suite harness, backup-stream metadata store/client abstractions, task scheduler, region checkpoint operations, encryption configuration, failpoints, TiKV test cluster utilities, PD safepoint state, and external local backup file layout. It is a high-level integration point between raftstore observers, backup-stream endpoints, metadata persistence, flushing, region checkpoint resolution, and gRPC control APIs.

## Risks And Edge Cases
The tests are timing-sensitive: several use sleeps to allow retries, flushes, or resolve operations. They rely on failpoint names matching production code. Some race tests only prove expected behavior in the test cluster timing model. The encryption test verifies absence of plain zstd headers and raw values, but does not fully decrypt and authenticate every byte. The memory quota assertion samples a metric in a failpoint callback, so it catches large overages but may miss short transient spikes outside the callback.

## Test Signals
The file itself is a test signal collection for backup-stream resilience. It validates retry after observer/initial-scan failure, nonblocking region operator handoff, memory quota enforcement, flush/commit/resolve ordering, encrypted temp-file spill behavior, pause/error metadata shape, safepoint preservation after fatal errors, and idempotent force flush while a flush is pending.
