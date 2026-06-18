<!-- BEGIN_FILE_RESEARCH: sources/storage-engines/foundationdb/bindings/java/src/main/com/apple/foundationdb/testing/WorkloadContext.java -->
# sources/storage-engines/foundationdb/bindings/java/src/main/com/apple/foundationdb/testing/WorkloadContext.java

## Purpose
`WorkloadContext` is a JNI wrapper exposing simulation/workload context values to Java workload code.

## Important APIs, Types, And Functions
It stores a native `impl` pointer and exposes `getProcessID`, `setProcessID`, `getClientID`, `getClientCount`, `getSharedRandomNumber`, and overloaded `getOption` for string, long, boolean, and double defaults. All operations delegate to native methods.

## Control Flow, State, And Persistence
The Java object has minimal local state. Calls cross into native code to read or mutate workload context; `setProcessID` affects context used by executor threads in `AbstractWorkload`.

## Dependencies And Integration Points
It is consumed by `AbstractWorkload` and native simulation bindings. Private construction implies native or reflective instantiation.

## Risks And Test Signals
Risks include invalid native pointer lifetime, option type mismatch, and thread context propagation. Tests should verify option defaults, client identity values, process ID set/get, and behavior under executor callbacks.
<!-- END_FILE_RESEARCH: sources/storage-engines/foundationdb/bindings/java/src/main/com/apple/foundationdb/testing/WorkloadContext.java -->
