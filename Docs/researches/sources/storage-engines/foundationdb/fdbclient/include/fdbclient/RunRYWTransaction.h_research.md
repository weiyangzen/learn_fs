# sources/storage-engines/foundationdb/fdbclient/include/fdbclient/RunRYWTransaction.h

## Purpose
`RunRYWTransaction.h` defines coroutine helpers that run a caller-supplied function inside a `ReadYourWritesTransaction` retry loop. It is the convenience layer for idempotent transactional code that wants automatic commit and retry handling.

## Important APIs, Types, And Functions
- `RunRYWTransactionResult<Function>` infers the future value returned by a callback taking `Reference<ReadYourWritesTransaction>`.
- `runRYWTransaction()` retries forever on errors handled by `tr->onError()`.
- `runRYWTransactionDebug()` additionally logs the callback name and committed version on success.
- `runRYWTransactionVoid()` handles callbacks returning `Future<Void>`.
- `runRYWTransactionFailIfLocked()` propagates `database_locked` instead of retrying it.
- `runRYWTransactionNoRetry()` runs callback and commit exactly once.

## Control Flow And State
Each helper creates one `Reference<ReadYourWritesTransaction>` before the loop. The loop awaits callback result, commits, returns result, catches `Error`, and awaits `onError()` to reset/retry. The no-retry variant omits catch/onError. The fail-if-locked variant checks the error code before retry handling.

## Persistence And External State
Persistence occurs through the transaction commit itself. Debug mode emits `TraceEvent("DebugRunRYWTransaction")` with function name and commit version.

## Dependencies And Integration Points
It depends on Flow coroutines, generic `RunTransaction.h`, and `ReadYourWrites.h`. It integrates with all APIs expecting automatic RYW transaction retries and with callback code that must be idempotent under retry.

## Risks And Edge Cases
The callback must be idempotent because it can run multiple times. Reusing the same transaction reference across retries relies on `onError()` to reset all transaction-local state correctly. Functions returning references into transaction arenas should not outlive the transaction unexpectedly. `runRYWTransactionDebug()` requires a meaningful function name from the caller.

## Test Signals
Tests should cover successful return values, void callbacks, retry after retriable errors, propagation of non-retriable or locked errors where intended, no-retry behavior, callback idempotency assumptions, debug trace emission, and option/state reset across retries.
