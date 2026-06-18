# sources/storage-engines/foundationdb/fdbserver/grvproxy/GrvQueueDelay.cpp

## Purpose
Implements queue accounting and delay-estimation helpers for GRV proxy `maxGrvQueueDelayMS` rejection.

## Important APIs, Types, and Functions
- `GrvQueueTransactionCounts::add/remove(TransactionPriority, int64_t)` mutates per-priority queued counts with assertions.
- Request overloads adapt `GetReadVersionRequest`.
- `normalRateQueuedTransactions()` returns system plus default queued work.
- `batchRateQueuedTransactions()` returns system plus default plus batch queued work.
- `estimateRemainingGrvQueueDelay(...)` asks normal and, for batch requests, batch `GrvTransactionRateInfo` objects for delay estimates.
- `shouldRejectForMaxGrvQueueDelay(...)` implements option/lease/elapsed-delay threshold rejection.

## Control Flow
Priority accounting maps immediate-and-above to system, default-and-above to default, and lower priorities to batch. Delay estimation always computes normal-rate delay and computes batch-rate delay only for batch-priority work. Rejection ignores absent options, rejects bounded requests on expired lease, otherwise compares clamped elapsed delay plus remaining delay to the millisecond threshold.

## State and Persistence Behavior
State is caller-owned in-memory counters and request metadata only. No persistence.

## Dependencies and Integration Points
Depends on `GetReadVersionRequest`, `TransactionPriority`, `GrvTransactionRateInfo`, Flow time, and assertions. Used by `GrvProxyServer.cpp` at queue insertion/removal/start boundaries.

## Risks and Edge Cases
Remove asserts catch accounting mismatches. Batch requests must consider both normal and batch delay. Expired leases reject bounded requests regardless of numeric delay. Future timestamps are clamped to avoid negative elapsed contribution.

## Test Signals
`GrvQueueDelayTests.cpp` covers accounting, estimates, disabled rate info, and rejection decisions.
