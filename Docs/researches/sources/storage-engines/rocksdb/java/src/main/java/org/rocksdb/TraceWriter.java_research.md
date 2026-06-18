# sources/storage-engines/rocksdb/java/src/main/java/org/rocksdb/TraceWriter.java

## Purpose
`TraceWriter` is a Java interface for exporting RocksDB trace records to an arbitrary sink.

## Important APIs and Types
It declares `write(Slice data)`, `closeWriter()`, and `getFileSize()`. `write` and close can throw `RocksDBException`.

## Control Flow
Trace infrastructure calls `write` for each trace data slice, queries size through `getFileSize`, and calls `closeWriter` to finish the sink.

## State and Persistence Behavior
The interface owns no state. Implementations define persistence behavior, such as writing to files, streams, or remote systems. `getFileSize` is part of trace-size limiting.

## Dependencies and Integration Points
It depends on `Slice` and `RocksDBException` and integrates with tracing APIs via `AbstractTraceWriter`.

## Risks and Test Signals
Tests for implementations should cover slice lifetime, partial write failures, close failures, size accounting, and idempotent close behavior. Implementations must not retain a native `Slice` beyond its valid callback lifetime unless copied.
