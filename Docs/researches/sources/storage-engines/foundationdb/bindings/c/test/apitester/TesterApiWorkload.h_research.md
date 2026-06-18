# sources/storage-engines/foundationdb/bindings/c/test/apitester/TesterApiWorkload.h

## Purpose
`TesterApiWorkload.h` declares `ApiWorkload`, the base class for randomized C API tester workloads. It exposes lifecycle hooks, progress-control integration, random data helpers, common mutation operations, tenant helpers, and the in-memory expected-state stores.

## Important APIs, Types, And Functions
- `ApiWorkload : public WorkloadBase, IWorkloadControlIfc`.
- Public overrides: `start()`, `getControlIfc()`, `stop()`, and `checkProgress()`.
- Extension points: `setup(TTaskFct cont)`, `runTests()`, and `randomOperation(TTaskFct cont)`.
- Protected configuration fields include API version, key/value lengths, max keys per transaction, initial size, existing-key ratio, operation counts, stop/progress atomics, key prefix, tenant names, and `stores`.
- Protected helpers cover random key/value generation, data population/clearing, common random insert/clear/clear-range operations, and tenant mapping.

## Control Flow
The header defines the contract implemented by `TesterApiWorkload.cpp`: derived classes override `randomOperation()` or `runTests()`, and call protected helpers with continuations to keep the scheduler-driven asynchronous flow alive.

## State And Persistence Behavior
The declared fields define both persistent key scope (`keyPrefix`, tenants) and local state (`stores`, atomics, operation counters). Persistent effects are performed by implementation methods and derived workloads.

## Dependencies And Integration Points
It includes `TesterWorkload.h`, `TesterKeyValueStore.h`, and `<atomic>`. API tester workload files register concrete factories against this base.

## Risks And Edge Cases
Because `ApiWorkload` also implements `IWorkloadControlIfc`, callers must only request the control interface when `runUntilStop` is true. Derived classes must always schedule or invoke their continuation, or the workload stalls.

## Test Signals
Header correctness is compile-tested by all API tester workloads. Runtime signals come from derived workload progress checks and expected-state assertions.
