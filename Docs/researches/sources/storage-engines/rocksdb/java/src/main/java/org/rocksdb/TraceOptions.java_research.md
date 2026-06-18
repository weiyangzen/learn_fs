# sources/storage-engines/rocksdb/java/src/main/java/org/rocksdb/TraceOptions.java

## Purpose
`TraceOptions` configures trace capture, currently by bounding maximum trace file size.

## Important APIs and Types
The default constructor sets `maxTraceFileSize` to 64 GiB. The alternate constructor accepts a byte count. `getMaxTraceFileSize()` exposes the value.

## Control Flow
There is no native logic in this class. `RocksDB.startTrace(TraceOptions, AbstractTraceWriter)` consumes the value when trace writing starts.

## State and Persistence Behavior
It is an immutable value object. It does not write traces itself; it only constrains trace output size in the tracing subsystem.

## Dependencies and Integration Points
It integrates with `RocksDB#startTrace` and trace-writer abstractions such as `AbstractTraceWriter`/`TraceWriter`.

## Risks and Test Signals
Tests should cover default size, custom sizes, zero/negative handling at consuming APIs, and enforcement by trace writers. Since Java does no validation, native/startTrace validation must guard nonsensical sizes.
