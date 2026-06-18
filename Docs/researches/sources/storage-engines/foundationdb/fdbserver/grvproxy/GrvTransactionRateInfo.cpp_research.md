# sources/storage-engines/foundationdb/fdbserver/grvproxy/GrvTransactionRateInfo.cpp

## Purpose
Implements smoothed transaction-rate limiting for GRV proxy release windows.

## Important APIs, Types, and Functions
- Constructor initializes window, empty-queue budget cap, rate, and smoothers.
- `canStart(...)` checks `numAlreadyStarted + count` against `min(limit + budget, START_TRANSACTION_MAX_TRANSACTIONS_TO_START)`.
- `estimateDelay(...)` returns zero if startable or disabled, infinity if active rate is zero, otherwise deficit/rate.
- `endReleaseWindow(...)` updates budget, caps budget when queues are empty, and records released count.
- `disable()` marks disabled and smoothly targets rate zero.
- `setRate(...)` validates and updates current/smoothed rate.
- `startReleaseWindow()` derives `limit` from smoothed target rate minus smoothed release rate.
- `/GrvTransactionRateInfo/Simple` tests throttling under an over-eager mock client.

## Control Flow
GRV proxy calls `startReleaseWindow`, uses `canStart` while draining queues, then calls `endReleaseWindow`. Ratekeeper replies call `setRate`; lease expiry calls `disable`.

## State and Persistence Behavior
All state is in-memory: rate window, budget cap, rate, computed limit, budget, disabled flag, and smoothers.

## Dependencies and Integration Points
Depends on `fdbrpc/Smoother`, server knobs, Flow unit tests, and GRV proxy queue draining. Used by `GrvQueueDelay` for delay estimates.

## Risks and Edge Cases
Budget can accumulate or compensate for overuse. Limit can become negative. Disabled returns zero estimated delay, while active zero rate returns infinity. The max-start knob caps capacity independently of rate math. Invalid rates assert.

## Test Signals
The included unit test verifies a client attempting 20 TPS is throttled to roughly 10 TPS over 60 seconds.
