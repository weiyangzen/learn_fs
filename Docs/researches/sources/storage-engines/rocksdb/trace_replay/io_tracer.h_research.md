# sources/storage-engines/rocksdb/trace_replay/io_tracer.h

## Purpose

Declares IO tracing types for capturing file-system operations in RocksDB trace files.

## Important APIs, Control Flow, And Dependencies

`IOTraceOp` defines bit positions for optional record fields: file size, length, and offset. `IOTraceRecord` contains required operation fields, optional data fields, and debug context fields, with constructors for general/file-size and length/offset records. `IOTraceHeader`, `IOTraceWriter`, `IOTraceReader`, and `IOTracer` declare the writer, reader, and lifecycle controller APIs.

## State, Persistence, Integration, Risks, And Test Signals

Trace records persist through a user-provided `TraceWriter` in the same `Trace` envelope used by other trace replay code. The file-system integration is through `IODebugContext` and RocksDB file-system wrappers that decide which `io_op_data` bits are present. `IOTracer` maintains both an atomic writer pointer and a `tracing_enabled` boolean used as a cheaper check by file-system classes, with comments explaining race tolerance. Risks include bit-position compatibility when adding new optional fields, request-id pointer lifetime in `IODebugContext`, and callers needing to match `io_op_data` to populated fields. Tests validate field round trips and tracing lifecycle behavior.
