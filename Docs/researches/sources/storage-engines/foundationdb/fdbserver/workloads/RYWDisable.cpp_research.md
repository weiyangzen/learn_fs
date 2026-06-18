## sources/storage-engines/foundationdb/fdbserver/workloads/RYWDisable.cpp

`RYWDisableWorkload` verifies that `READ_YOUR_WRITES_DISABLE` cannot be set after a `ReadYourWritesTransaction` has performed operations that require the RYW layer. It runs on client 0 for `testDuration`, choosing random operation prefixes before attempting to disable RYW and checking whether that should succeed.

Important APIs are `ReadYourWritesTransaction`, `FDBTransactionOptions::READ_YOUR_WRITES_DISABLE`, `error_code_client_invalid_operation`, Flow retry handling, and the workload's `keyForIndex` generator. The generated keys are fixed length and ordered by embedding a double-derived index.

The `_start` loop creates a RYW transaction, randomly performs one of: `set`, asynchronous `get` without waiting, awaited `get`, or no-op. For the first three cases it expects setting `READ_YOUR_WRITES_DISABLE` to throw `client_invalid_operation`; for no-op it expects success. It then delays, checks duration, optionally resets the transaction, and continues.

No data is committed, so persistence is minimal. Runtime state is only timing and generated transaction operations. Risks include the no-wait get case depending on client-side state being marked immediately after issuing the future, and the workload not tracking the `clients` vector it checks. It deliberately does not validate database contents.

Integration points are NativeAPI transaction option validation and RYW transaction internal state. Test signals are assertions around expected option-setting behavior; `check` returns false only if any stored client future is in error, but the main path returns directly from `_start`.
