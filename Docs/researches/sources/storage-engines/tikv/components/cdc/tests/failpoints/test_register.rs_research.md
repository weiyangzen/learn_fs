# sources/storage-engines/tikv/components/cdc/tests/failpoints/test_register.rs

## Purpose
`test_register.rs` validates CDC registration and deregistration behavior across pending batches, role changes, stale region epochs, splits, merges, and pending downstream removal.

## Important APIs, Types, and Functions
Tests use `TestSuite`, `new_event_feed`, `ObserverContext`, `RoleObserver::on_role_change`, `RegionEpoch`, and raftstore merge/split helpers. Failpoints include `cdc_incremental_scan_start`, `before_handle_catch_up_logs_for_merge`, `destroy_peer`, `before_schedule_resolver_ready`, and `raft_on_capture_change`.

## Control Flow
The suite pauses incremental scans or resolver readiness, mutates region topology, and asserts registration outcomes. `test_failed_pending_batch` confirms an epoch-not-match pending batch does not prevent re-subscription. `test_region_ready_after_deregister` simulates role loss while initialization is paused and verifies no panic. `test_connections_register` covers stale epoch rejection, connection replacement, and split error delivery. `test_merge` walks source/target subscriptions through prepare/commit merge and retry. The pending-downstream test checks deregistration during resolver build.

## State and Persistence Behavior
The tests exercise in-memory endpoint delegate/downstream state over real raftstore topology changes. Region metadata and MVCC writes live in the test cluster; CDC registrations are expected to be removed or replaced cleanly.

## Dependencies and Integration Points
Coverage spans service event feeds, observer role-change callbacks, endpoint registration validation, incremental scanner, resolver-ready scheduling, raftstore split/merge paths, and error conversion to CDC protocol errors.

## Risks and Edge Cases
Races between registration, initialization, and topology changes can leave stale delegates or send wrong errors. Merge handling is especially sensitive because source regions may be destroyed while target regions need epoch-not-match signaling.

## Test Signals
Expected signals include `Initialized`, `epoch_not_match`, and `region_not_found` events, plus absence of panics when a region becomes ready after deregistration. Some function naming appears typoed (`est_connections_registertest_deregister_pending_downstream`) but still carries the `#[test]` attribute.
