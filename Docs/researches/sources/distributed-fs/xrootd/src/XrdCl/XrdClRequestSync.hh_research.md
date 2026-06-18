# sources/distributed-fs/xrootd/src/XrdCl/XrdClRequestSync.hh

## Purpose

This header implements `RequestSync`, a small semaphore-based helper for running a fixed number of asynchronous or threaded requests with a concurrency quota and waiting for all completions.

## Important APIs, Types, And Functions

The constructor accepts total request count and parallel quota. `WaitForQuota()` blocks until a quota slot is available. `TaskDone(success)` releases a quota slot, decrements remaining count, optionally increments failure count, and posts the completion semaphore when all requests are done. `WaitForAll()` waits for total completion. `FailureCount()` returns the number of failed tasks.

## Control Flow

Callers typically loop over requests, call `WaitForQuota` before launching each one, and call `TaskDone` from each completion path. A separate caller can call `WaitForAll` to block until `pRequestsLeft` reaches zero. If `reqTotal` is zero, the constructor posts the total semaphore immediately.

## State And Persistence Behavior

State is in-memory: two heap-allocated `XrdSysSemaphore` objects, `pRequestsLeft`, `pFailureCounter`, and a mutex for updates. Copy and assignment are private and undefined to prevent accidental copying.

## Dependencies And Integration Points

The class depends only on `XrdSysPthread.hh`. It is useful in higher-level client batch operations that need bounded parallelism without adopting a full task framework.

## Risks And Edge Cases

`FailureCount()` reads `pFailureCounter` without locking, so concurrent reads during active completions may race. If a launched task never calls `TaskDone`, both quota and total waits can block forever. Quota zero would create a semaphore that never permits launches.

## Test Signals

Tests should cover zero total requests, quota limiting, success/failure counts, all-completion wakeup, and misuse cases such as missing `TaskDone` or zero quota under timeout-controlled tests.
