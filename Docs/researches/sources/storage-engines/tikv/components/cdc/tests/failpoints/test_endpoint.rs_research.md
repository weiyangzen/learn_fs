# sources/storage-engines/tikv/components/cdc/tests/failpoints/test_endpoint.rs

## Purpose
`test_endpoint.rs` exercises CDC endpoint behavior under failpoint-controlled races: incremental scan cancellation/failure, ordering before snapshot initialization, old-value-cache updates, RawKV resolved-ts bounds, stream multiplexing readiness, pending-region errors, and unresolved-region accounting.

## Important APIs, Types, and Functions
The tests use `TestSuite`/`TestSuiteBuilder`, `new_event_feed`/`new_event_feed_v2`, raftstore split/merge helpers, PD TSO, raw KV clients, and `Task::Validate` probes. Failpoints include `cdc_incremental_scan_start`, `cdc_scan_batch_fail`, `cdc_before_handle_multi_batch`, `cdc_sleep_before_drain_change_event`, `before_post_incremental_scan`, `cdc_before_initialize`, `before_schedule_incremental_scan`, and `before_schedule_resolver_ready`.

## Control Flow
Most tests open one or more event feeds, pause a specific endpoint stage, mutate the cluster, then unpause and assert emitted CDC events. The double-scan tests verify one of two concurrent scans handles deregistration or scan I/O failure without corrupting the surviving downstream. Ordering tests pause multi-batch handling and sink draining so they can assert `Initialized` arrives after prior delta entries. Multiplexing subscribes the same region twice with different request IDs and verifies resolved-ts routing waits for each request to become ready.

## State and Persistence Behavior
The tests manipulate real in-memory raftstore clusters and MVCC state, but do not persist artifacts. They inspect endpoint state using validation tasks for old-value cache update counts and unresolved-region counts.

## Dependencies and Integration Points
Coverage crosses service streams, endpoint delegates, resolver readiness, incremental scanner, CDC sink/channel flow, RawKV API V2 causal timestamp provider, and raftstore split/merge notifications.

## Risks and Edge Cases
The suite targets races that can duplicate events, emit resolved-ts before initialization, lose region errors while pending, or leave unresolved-region counts stuck. Timing uses sleeps around failpoints, so reliability depends on failpoints being at stable boundaries.

## Test Signals
Assertions check region-not-found/epoch-not-match/congested errors, initialized event placement, resolved-ts request IDs and timestamp bounds, old-value cache update suppression when no captures remain, and unresolved-region count transitioning from all pending to zero.
