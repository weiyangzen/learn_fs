# sources/storage-engines/rocksdb/trace_replay/io_tracer.cc

## Purpose

Implements RocksDB IO operation tracing: a binary writer/reader for file-system operation records and an `IOTracer` controller that starts, stops, and writes IO trace records.

## Important APIs, Control Flow, And Dependencies

`IOTraceWriter::WriteIOOp` enforces max trace file size, writes core fields (`io_op_data`, operation name, latency, status, file name), then serializes optional fields according to the set bits in `io_op_data`: file size, length, and offset. It also serializes `IODebugContext` trace data, currently request ID. `WriteHeader` emits a `kTraceBegin` header with magic and RocksDB version. `IOTraceReader` decodes the same format and returns `Incomplete` statuses for missing fields. `IOTracer::StartIOTrace` installs a new `IOTraceWriter`, sets `tracing_enabled`, and writes a header; `EndIOTrace` deletes it; `WriteIOOp` double-checks writer presence under a mutex and ignores writer errors with `PermitUncheckedError`.

## State, Persistence, Integration, Risks, And Test Signals

The controller stores trace options, an atomic raw writer pointer, mutex, and a non-atomic `tracing_enabled` fast path deliberately annotated for TSAN suppression in the header. Dependencies include RocksDB `TraceWriter`/`TraceReader`, `TraceOptions`, `IODebugContext`, `IOStatus`, `SystemClock`, coding helpers, and trace replay encoding. Risks include raw pointer ownership, ignored write errors at the tracer wrapper layer, use of `log2` to find bit positions, asserts rather than graceful errors for unknown future bits, and no trailing-payload validation. Tests in `io_tracer_test.cc` cover optional-field combinations, request ID, start/stop behavior, and multiple records.
