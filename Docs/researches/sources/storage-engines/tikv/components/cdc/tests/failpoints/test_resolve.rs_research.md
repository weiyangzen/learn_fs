# sources/storage-engines/tikv/components/cdc/tests/failpoints/test_resolve.rs

## Purpose
`test_resolve.rs` validates resolved-ts behavior when resolvers become stale, regions merge, callbacks are dropped, or raft configuration changes make progress temporarily impossible.

## Important APIs, Types, and Functions
The suite uses `TestSuite`, `TestSuiteBuilder`, event feeds, PD TSO, prewrite/commit, merge/confchange helpers, and `ReadableDuration` CDC config tuning. Failpoints include `before_schedule_resolver_ready`, `cdc_incremental_scan_start`, `cdc_before_handle_multi_batch`, `cdc_before_handle_deregister`, and `change_peer_after_update_region`.

## Control Flow
`test_stale_resolver` pauses resolver readiness, opens replacement streams, commits while another scan is paused, and then verifies both streams receive the correct prewrite/commit/initialized combinations. `test_region_error` blocks multi-batch and deregister handling while merging regions, then confirms the target region still receives monotonically increasing resolved-ts. `test_joint_confchange` repeatedly receives resolved-ts across node stop/start and joint confchange, then pauses region update during another confchange and expects resolved-ts progress to stop within the timeout.

## State and Persistence Behavior
The state under test is resolver lifecycle and resolved-ts advancement, plus raftstore region/peer metadata in the test cluster. No research or product state is persisted by the tests.

## Dependencies and Integration Points
The tests connect endpoint resolver scheduling, CDC event emission, raftstore merge/confchange, PD client operations, and hibernate-region compatibility settings.

## Risks and Edge Cases
Stale resolvers can emit incorrect events after connection replacement. Region errors can drop callbacks needed for resolved-ts advancement. Joint consensus changes can make resolved-ts unsafe to advance if region metadata is blocked or peers are unavailable.

## Test Signals
Assertions require commit/prewrite/initialized event shapes without CDC errors, strictly increasing or nondecreasing resolved-ts in healthy phases, and no resolved-ts progress while a critical region update failpoint is paused.
