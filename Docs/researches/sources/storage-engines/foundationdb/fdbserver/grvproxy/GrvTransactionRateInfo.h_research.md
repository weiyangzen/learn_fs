# sources/storage-engines/foundationdb/fdbserver/grvproxy/GrvTransactionRateInfo.h

## Purpose
Declares the GRV proxy transaction-rate limiter and documents its release-window model.

## Important APIs, Types, and Functions
- Constructor initializes limiter parameters.
- `startReleaseWindow()` computes allowed releases for the window.
- `canStart(...)` tests if more transactions can be released.
- `estimateDelay(...)` predicts when the same arguments become startable.
- `endReleaseWindow(...)` adjusts budget and smoothing after a drain pass.
- `setRate(...)`, `disable()`, `getRate()`, and `getLimit()` expose ratekeeper update and stats hooks.

## Control Flow
Expected lifecycle is rate updates through `setRate`, repeated `startReleaseWindow`/`canStart`/`endReleaseWindow` cycles, and `disable` on stale rate leases.

## State and Persistence Behavior
Private state is memory-only: rate window, empty-queue budget cap, rate, limit, budget, disabled flag, and two smoothers.

## Dependencies and Integration Points
Depends on `fdbrpc/Smoother`. Used by `GrvProxyServer.cpp` for normal and batch queues and by `GrvQueueDelay` for estimates.

## Risks and Edge Cases
Disabled, zero-rate, empty-queue budget capping, and call ordering have distinct semantics; callers must follow the release-window protocol.

## Test Signals
Implementation includes a simple throttling unit test, with additional indirect coverage from queue-delay tests.
