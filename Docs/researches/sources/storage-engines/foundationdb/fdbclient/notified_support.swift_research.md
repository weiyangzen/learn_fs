# sources/storage-engines/foundationdb/fdbclient/notified_support.swift

## Purpose
This Swift file is currently a placeholder for Swift helpers around Flow/FDB notification primitives. It imports `Flow`, `flow_swift`, and `FDBClient`, but the only implementation is commented out.

## Important APIs, Types, And Functions
The commented extension targets `NotifiedVersion` and would add an async `atLeast(_:)` wrapper around `whenAtLeast(limit)`, awaiting a `FutureVoid` through Swift concurrency.

## Control Flow
No executable control flow is compiled. The intended path was: call `whenAtLeast`, receive a Flow future, bridge it to `await f.value()`, and propagate errors.

## State And Persistence Behavior
There is no runtime state or persistence. If enabled, the helper would observe version-notification state owned by `NotifiedVersion` without mutating durable data.

## Dependencies And Integration Points
The imports show integration between generated Swift bindings and Flow futures. The file is a natural bridge point for async/await support in the Swift API.

## Risks And Edge Cases
Because the code is commented, the risk is mostly build churn or stale API expectations: `VersionMetricHandle.ValueType`, `FutureVoid`, or `value()` signatures may no longer match. If uncommented, cancellation/error propagation across Flow and Swift concurrency would need tests.

## Test Signals
Current test signal is simply successful Swift compilation with unused imports accepted. Future tests should verify `atLeast` completes after the notified version crosses the limit and propagates failed/cancelled futures.
