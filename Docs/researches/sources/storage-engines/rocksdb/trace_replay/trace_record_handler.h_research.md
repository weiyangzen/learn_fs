# sources/storage-engines/rocksdb/trace_replay/trace_record_handler.h

## Purpose

Declares the execution handler for replaying `TraceRecord` objects against a RocksDB `DB`.

## Important APIs, Control Flow, And Dependencies

`TraceExecutionHandler` derives from `TraceRecord::Handler` and overrides handling for write, get, iterator seek, and multiget records. It stores `DB*`, a CF-ID-to-handle map, read/write options, and a system clock pointer. The constructor requires a DB and a non-empty vector of column-family handles.

## State, Persistence, Integration, Risks, And Test Signals

The header shows that replay is stateful because writes apply to the DB and all operations measure execution timestamps. It integrates directly with the trace record class hierarchy and result classes. The `TODO` notes a separate analyzer handler, which in this source set is implemented independently by `TraceAnalyzer` rather than here. Risks are non-owning DB/handle lifetimes and CF ID lookup failures. Test signals are indirect through replay and analyzer behavior.
