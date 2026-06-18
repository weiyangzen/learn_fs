# sources/storage-engines/foundationdb/bindings/c/test/apitester/tests/CApiCancelTransactionWithTimeout.toml

## Purpose
Adds randomized transaction timeouts to the cancel-transaction workload.

## Important APIs, types, and functions
Configures `CancelTransaction` with `minTxTimeoutMs = 10` and `maxTxTimeoutMs = 10000`, causing `WorkloadBase` to set `FDB_TR_OPTION_TIMEOUT`.

## Control flow
Timeouts may occur during cancellation and buggified errors; the executor restarts timeout-capable transactions.

## State and persistence behavior
Only workload data persists; timeout/retry state is client-side.

## Dependencies and integration points
Stresses `WorkloadBase::doExecute`, transaction timeout options, executor `onError`, and cancel logic.

## Risks and test signals
Risks include treating expected timeouts as fatal or retrying writes without conflict protection. Passing indicates robust timeout/cancel interaction.
