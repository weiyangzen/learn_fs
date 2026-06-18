# sources/storage-engines/foundationdb/fdbserver/grvproxy/GrvQueueDelayTests.cpp

## Purpose
Flow unit tests for GRV proxy maximum queue-delay logic: queue count aggregation, delay estimation, disabled limiter behavior, and threshold semantics.

## Important APIs, Types, and Functions
- `forceLinkGrvQueueDelayTests()` provides a link anchor.
- `makeRateInfo()` constructs a rate-10 active release-window limiter.
- `expectedEstimateDelay(...)` mirrors expected deficit/rate calculation.
- `expectedShouldReject(...)` mirrors option, lease, elapsed, and threshold logic.
- Test cases cover queue counts, estimate tables, disabled rate info, and rejection decision tables.

## Control Flow
Tests create immediate/default/batch requests and validate direct and aggregate counts. Estimate cases seed counts and compare helper output with expected normal and optional batch delay. Rejection cases vary option presence, request-time offsets, remaining delay, and lease state.

## State and Persistence Behavior
In-memory test state only; timestamps are relative to `now()`.

## Dependencies and Integration Points
Depends on `GrvQueueDelay.h`, server knobs, and `flow/UnitTest.h`. Targets the helper behavior used before GRV proxy queue insertion.

## Risks and Edge Cases
Encodes that equal-to-threshold is accepted, over-threshold rejected, absent option accepted even with expired lease, expired lease rejects bounded requests, and future timestamps are clamped.

## Test Signals
Primary regression tests for the queue-delay feature, though they do not exercise full actor concurrency.
