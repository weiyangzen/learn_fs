<!-- BEGIN_FILE_RESEARCH: sources/storage-engines/foundationdb/bindings/java/src/main/com/apple/foundationdb/testing/AbstractWorkload.java -->
# sources/storage-engines/foundationdb/bindings/java/src/main/com/apple/foundationdb/testing/AbstractWorkload.java

## Purpose
`AbstractWorkload` is a base class for Java workloads driven by FoundationDB's native simulation/testing infrastructure.

## Important APIs, Types, And Functions
It stores a `WorkloadContext`, creates a small `ThreadPoolExecutor`, exposes `getExecutor`, declares abstract `setup`, `start`, and `check` methods taking `Database` and `Promise`, and provides overridable `getMetrics` and `getCheckTimeout`. Static `log` delegates to a native logger.

## Control Flow
The constructor captures the current process ID and creates an executor whose `beforeExecute` restores that process ID in the context before running work. Subclasses implement lifecycle phases and can use the executor for async tasks.

## State And Persistence Behavior
State is the workload context and executor. Persistence is external through database operations performed by subclasses and native logging. `shutdown` exists but is private, implying lifecycle may be managed reflectively or by native code.

## Dependencies And Integration Points
It depends on `Database`, `Promise`, `PerfMetric`, `WorkloadContext`, Java concurrency types, and native JNI functions. The testing harness likely instantiates subclasses from the simulation workload engine.

## Risks And Test Signals
Risks include executor leaks if `shutdown` is not invoked, native logger initialization, process ID propagation across threads, and no bounded queue due to `SynchronousQueue`. Tests should verify lifecycle callbacks, promise completion, metrics collection, and native integration behavior.
<!-- END_FILE_RESEARCH: sources/storage-engines/foundationdb/bindings/java/src/main/com/apple/foundationdb/testing/AbstractWorkload.java -->
