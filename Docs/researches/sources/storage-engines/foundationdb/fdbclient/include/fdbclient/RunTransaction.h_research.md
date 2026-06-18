# sources/storage-engines/foundationdb/fdbclient/include/fdbclient/RunTransaction.h

## Purpose
`RunTransaction.h` provides generic coroutine retry helpers for database-like objects that create transaction references. It also defines a wrapper for system-key transactions that automatically applies system, priority, and lock-aware options.

## Important APIs, Types, And Functions
- `transaction_option_setter` and `can_set_transaction_options` detect DB wrappers that should set options before each attempt.
- `RunTransactionResult<Function, DB>` infers callback result type.
- `runTransaction()` and `runTransactionVoid()` create a transaction, run callback, commit, return, and retry through `onError()`.
- `SystemTransactionGenerator<DB>` wraps another DB reference, creates its transactions, and sets read/write system key, immediate priority, and lock-aware options.
- `SystemDB()` and `SystemDBWriteLockedNow()` are convenience factories.

## Control Flow And State
On every retry loop, the helper calls `db->setOptions(tr)` if the DB type participates in `transaction_option_setter`. It awaits callback and commit through `safeThreadFutureToFuture`, catches Flow `Error`, and awaits `tr->onError(err)` before retrying.

## Persistence And External State
The helper itself is stateless beyond the transaction reference and wrapper booleans. Persistent effects are the user's mutations after a successful commit. The system wrapper can access and modify system keys depending on `write`.

## Dependencies And Integration Points
It depends on Flow futures/coroutines and generated transaction option enums. It integrates with thread-safe transaction implementations because commits and `onError()` are converted through `safeThreadFutureToFuture`.

## Risks And Edge Cases
Callbacks must be idempotent. Options are set before each attempt, so non-persistent options in the transaction implementation must tolerate repeated setting. The result type depends on `getValue()`, so callback return types must match FoundationDB future conventions. System transactions can bypass normal key protections if constructed with write access.

## Test Signals
Tests should cover generic DB wrappers, option setter detection for raw and `Reference<T>` types, retry semantics, void and non-void callbacks, thread-future conversion, system-key read/write options, immediate priority, lock-aware options, and `SystemDBWriteLockedNow()` all-true behavior.
