# sources/storage-engines/foundationdb/bindings/c/test/mako/future.hpp

## Purpose
Provides Mako helpers for waiting on FDB futures and converting operation/on-error outcomes into `OK`, `RETRY`, or `ABORT`.

## Important APIs, types, and functions
`FutureRC`, `LogContext`, `NoLog`, `waitFuture`, `handleForOnError`, `waitAndHandleForOnError`, and `waitAndHandleError` are the public helpers.

## Control flow
Helpers block for readiness, inspect `f.error()`, log according to expected timeout/retryable classification, call `tx.onError` when needed, and reset transactions on unretryable `onError` results.

## State and persistence behavior
No persistent state is owned, but helpers mutate caller transaction state by invoking `onError` or `reset`.

## Dependencies and integration points
Depends on `fdb_api.hpp`, Mako logger, and `force_inline`. Used by Mako synchronous and async operation loops.

## Risks and test signals
Incorrect error classification changes retry/abort behavior and benchmark counters. Assertions assume block-level errors are not retryable.
