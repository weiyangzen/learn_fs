# sources/storage-engines/foundationdb/fdbserver/grvproxy/GrvQueueDelay.h

## Purpose
Declares GRV queue-delay accounting and rejection interfaces used to enforce client-specified maximum queue delay.

## Important APIs, Types, and Functions
- `GrvQueueTransactionCounts` stores queued transaction counts for system, default, and batch priorities.
- `GrvQueueDelayEstimate` contains required `normalRateDelay` and optional `batchRateDelay`.
- `GrvRateLeaseState` models ratekeeper lease state as `Unknown`, `Active`, or `Expired`.
- `estimateRemainingGrvQueueDelay(...)` estimates delay against queue counts and normal/batch rate info.
- `shouldRejectForMaxGrvQueueDelay(...)` decides threshold rejection for a request.

## Control Flow
Callers maintain counts, estimate remaining delay for incoming/queued work, then ask the rejection helper using request metadata and optional lease state.

## State and Persistence Behavior
Structures are in-memory only and contain primitive counters/delay values.

## Dependencies and Integration Points
Includes commit/GRV proxy interfaces, `GrvTransactionRateInfo`, and Flow. Integrated mainly by `GrvProxyServer.cpp`.

## Risks and Edge Cases
The API accepts raw rate-info pointers, so callers must pass valid normal and batch limiters. Priority classification directly affects admission behavior.

## Test Signals
The matching test file covers every public helper and exposed count aggregation.
