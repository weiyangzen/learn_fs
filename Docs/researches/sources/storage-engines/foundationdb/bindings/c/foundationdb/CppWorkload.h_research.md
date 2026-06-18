# sources/storage-engines/foundationdb/bindings/c/foundationdb/CppWorkload.h

## Purpose
`CppWorkload.h` defines the C++ external workload interface for FoundationDB client/simulation testing. It gives workload authors abstract classes for logging, context access, promises, workload lifecycle, metrics, and factories.

## Important APIs, Types, And Functions
- Forward declarations expose `FDBFuture`, `FDBResult`, `FDBDatabase`, and `FDBTransaction`.
- `FDBSeverity` enumerates trace severities.
- `FDBLogger::trace()` is the abstract logging hook.
- `FDBWorkloadContext` provides process identity, simulated time, randomness, typed option getters, client ids, shared random number, and delayed futures.
- `FDBPromise` and templated `GenericPromise<T>` wrap asynchronous stage completion.
- `FDBPerfMetric` describes metrics with name, value, averaged flag, and format.
- `FDBWorkload` declares `init`, `setup`, `start`, `check`, `getMetrics`, and default `getCheckTimeout()`.
- `FDBWorkloadFactory::create()` constructs workloads by name.

## Control Flow
External C++ workload libraries implement `FDBWorkloadFactory`, create workloads, initialize them with context, and resolve `GenericPromise<bool>` objects as each stage finishes. `getCheckTimeout()` defaults to 3000 simulated seconds unless overridden.

## State And Persistence Behavior
This header owns no state. Implementations manage workload state and database effects. `GenericPromise<T>` stores a shared `FDBPromise` and forwards `send()` by pointer to the value.

## Dependencies And Integration Points
It depends on the C++ standard library and the C API opaque types. CMake builds `cpp_workloads` from sample workload sources and links them against `fdb_c`.

## Risks And Edge Cases
ABI stability is a concern because this is a C++ virtual interface, not a C ABI. Implementations must respect asynchronous lifecycle expectations and avoid blocking. `GenericPromise::send()` passes an address of a local `T` to the underlying promise implementation, so the implementation must copy synchronously.

## Test Signals
Compile/link coverage comes from `cpp_workloads`; runtime signals come from simulation/client-testing workloads loaded through this interface.
