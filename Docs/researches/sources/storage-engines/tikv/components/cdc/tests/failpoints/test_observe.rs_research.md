# sources/storage-engines/tikv/components/cdc/tests/failpoints/test_observe.rs

## Purpose
`test_observe.rs` focuses on raftstore observation ordering and duplicate/stale command handling around CDC subscriptions, especially when apply flushing is paused while connections churn.

## Important APIs, Types, and Functions
The primary active test is `test_observe_duplicate_cmd`, parameterized over API V1/V2. It uses event feeds, PD TSO, prewrite/commit operations, and failpoint `before_cdc_flush_apply`. A second `test_delayed_change_cmd` is currently not a Rust test but documents a delayed change-command scenario involving read-index/heartbeat filters.

## Control Flow
The active test subscribes a region, receives initialization, prewrites a key, then pauses CDC apply flushing before committing. While the commit is blocked, it opens two new connections and drops the old ones. After unpausing, the surviving connection must receive exactly the committed entry followed by initialized, and then continue receiving advancing resolved-ts events.

## State and Persistence Behavior
The test uses real raftstore/MVCC state for the prewrite and commit. CDC state under observation includes observer command queues, downstream registration changes, and resolver progress after connection churn.

## Dependencies and Integration Points
This suite exercises `CdcObserver` apply flushing, endpoint multi-batch handling, downstream initialization, event-feed transport, PD timestamp allocation, and API-version key formatting.

## Risks and Edge Cases
The target risk is duplicated or misordered command delivery when an apply batch is delayed while downstreams are removed and re-added. The expected event order also guards against emitting `Initialized` before older observed changes.

## Test Signals
Assertions verify initialization, prewrite delivery, combined committed+initialized output on the final connection, absence of CDC errors, and multiple nonzero resolved-ts advancements after the churn.
