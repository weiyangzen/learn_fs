# sources/storage-engines/foundationdb/flow/include/flow/IRateControl.h

## Purpose
`IRateControl.h` defines a generic asynchronous allowance interface plus simple speed-limited and unlimited implementations.

## Important APIs, Types, And Functions
`IRateControl` declares `getAllowance()`, `returnUnused()`, `killWaiters()`, `wakeWaiters()`, and reference counting. `SpeedLimit` implements a windowed budget limiter. `Unlimited` always grants immediately.

## Control Flow
`SpeedLimit::getAllowance()` replenishes budget based on elapsed time, subtracts requested units, returns immediately if budget remains nonnegative, or waits on either a stop promise or a delay until the budget recovers. `wakeWaiters()` swaps and resolves the stop promise; `killWaiters()` resolves it with an error.

## State And Persistence Behavior
`SpeedLimit` stores limit, window seconds, last update time, signed budget, and a waiter promise. The state is in-memory only and reference counted.

## Dependencies And Integration Points
It depends on Flow futures, `now()`, `delay()`, `Never()`, `Promise`, `ReferenceCounted`, and errors. `IAsyncFile` exposes optional rate control hooks, especially for cached files.

## Risks And Edge Cases
Negative `returnUnused()` is ignored for convenience. Large elapsed times guard against int overflow. The destructor wakes waiters with `Never()`, so lifetime changes can unblock callers. Budget arithmetic depends on Flow's time source.

## Test Signals
Tests should cover immediate grant, delayed grant timing, returning unused units, wake/kill waiters, destructor unblocking, overflow guard, and `Unlimited` no-op behavior.
