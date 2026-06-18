# sources/storage-engines/rocksdb/trace_replay/trace_record.cc

## Purpose

Implements concrete `TraceRecord` classes used after decoding raw trace envelopes: write, get, iterator seek, and multiget query records.

## Important APIs, Control Flow, And Dependencies

`TraceRecord` stores a timestamp and creates a `TraceExecutionHandler` for replay. `WriteQueryTraceRecord` owns a pinned write-batch representation and dispatches to `Handler::Handle`. `GetQueryTraceRecord` stores a CF ID and pinned key. `IteratorQueryTraceRecord` optionally stores lower and upper bounds; `IteratorSeekQueryTraceRecord` adds seek type, CF ID, and key, and maps seek type back to `TraceType`. `MultiGetQueryTraceRecord` owns vectors of CF IDs and pinned keys and returns vectors of slices for execution or analysis.

## State, Persistence, Integration, Risks, And Test Signals

The classes are in-memory decoded representations; persistence is in the original trace file, while `PinnableSlice` members preserve payload lifetimes after decode. Integration is through the visitor-style `Accept` methods and `TraceRecord::Handler` implementations such as `TraceExecutionHandler` and `TraceAnalyzer`. Risks include copying vectors on getters, ensuring pinned slices are cleared in destructors, and preserving lower/upper iterator bound lifetimes. Coverage is indirect through trace replay/analyzer tests that decode records and accept handlers.
