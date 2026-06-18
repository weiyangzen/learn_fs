# sources/storage-engines/tikv/components/cdc/tests/failpoints/test_memory_quota.rs

## Purpose
`test_memory_quota.rs` validates CDC behavior when resolver lock tracking, pending lock handling, or initial lock scanning exceed the configured CDC memory quota.

## Important APIs, Types, and Functions
The tests build a single-node cluster with a small `memory_quota`, disable event-size quota effects via `cdc_event_size`, create large-key prewrites, and use `Task::Validate(Validate::Region)` to verify delegate cleanup. Failpoints include `cdc_finish_scan_locks_memory_quota_exceed` and `cdc_incremental_scan_start`.

## Control Flow
Each test opens an event feed, arranges lock memory usage to fit or exceed the quota, receives events, and expects a congested CDC error once quota is exceeded. After the error, a validation task confirms the delegate for the region has been removed.

## State and Persistence Behavior
The state under test is endpoint memory accounting for locks and delegates, not persistent storage. MVCC locks are created through normal prewrite calls; quota overflow results in deregistration/cleanup rather than persisted CDC state changes.

## Dependencies and Integration Points
The suite connects CDC endpoint memory quota enforcement with resolver lock tracking, pending downstream initialization, initial scan lock loading, grpc event feeds, and raftstore test-cluster writes.

## Risks and Edge Cases
Large keys are used to make memory pressure deterministic. The tests intentionally make `CdcEvent` size zero so failures isolate lock/resolver memory paths. A regression could either miss the congested error or keep a delegate alive after an unrecoverable quota failure.

## Test Signals
Four tests cover resolver tracking overflow after normal initialization, overflow when finishing scan locks, overflow while locks are pushed to pending during paused scans, and overflow while scanning preexisting locks. All expect `Error.has_congested()` and delegate absence.
