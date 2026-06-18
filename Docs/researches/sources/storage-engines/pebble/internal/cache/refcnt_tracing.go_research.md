# sources/storage-engines/pebble/internal/cache/refcnt_tracing.go

## Purpose
This file implements the tracing build variant of cache value reference counting, retaining stack traces for every reference operation.

## Important APIs, Types, And Functions
`refcnt` contains `atomic.Int32`, a mutex, and `msgs`. `init`, `refs`, `acquire`, `release`, `trace`, and `traces` mirror the normal API while recording stack-bearing messages.

## Control Flow
Initialization stores the count and traces `"init"`. `acquire` increments, validates the new count, and traces `"acquire"`. `release` decrements, validates non-negative counts, traces `"release"`, and returns whether the count reached zero. `traces` joins all recorded messages under lock.

## State And Persistence Behavior
State is in-memory per value. Trace messages can grow with reference churn and are used for diagnostics in finalizer/leak reports.

## Dependencies And Integration Points
It depends on `runtime/debug`, `strings`, `sync`, `atomic`, and `errors`. It integrates with `Value` finalizers and `entry` value ownership.

## Risks And Edge Cases
Tracing materially increases allocation, locking, and stack-capture cost. It is restricted by build tag for debugging. It still enforces the same correctness checks as the normal refcount.

## Test Signals
There are no direct tests here. Its signal is build compatibility and richer error output when cache reference bugs are reproduced under `tracing`.
