# sources/storage-engines/rocksdb/java/src/main/java/org/rocksdb/ThreadStatus.java

## Purpose
`ThreadStatus` represents a native RocksDB thread-status snapshot for Java monitoring and diagnostics.

## Important APIs and Types
The private JNI constructor stores thread id, `ThreadType`, DB name, column-family name, `OperationType`, elapsed microseconds, `OperationStage`, operation properties, and `StateType`. Public getters expose fields. Static helpers call native functions to translate thread type, operation, elapsed time, stage, operation property names/values, and state into readable forms.

## Control Flow
JNI construction maps byte identifiers through enum `fromValue` methods, failing on unknown values. Static formatting/interpreting APIs pass enum byte values and property arrays back to native helper functions.

## State and Persistence Behavior
It is an immutable snapshot of current thread activity. It does not persist monitoring data. The `long[] operationProperties` array is returned directly, so callers can mutate the snapshot.

## Dependencies and Integration Points
It depends on `ThreadType`, `OperationType`, `OperationStage`, `StateType`, and native monitoring helpers. It is consumed by APIs that expose RocksDB thread status.

## Risks and Test Signals
Tests should cover enum mapping drift, null DB/CF names, property interpretation for each operation type, elapsed-time formatting, and direct array aliasing. Native additions to operations/stages/states must be mirrored in Java enums or construction will fail.
