# sources/storage-engines/rocksdb/tools/trace_analyzer_tool.h

## Purpose

Declares the trace analyzer's public tool entry point, option and statistics structures, and the `TraceAnalyzer` class that bridges decoded trace records to per-operation statistics.

## Important APIs, Control Flow, And Dependencies

`TraceOperationType` assigns analyzer IDs to get, write-batch suboperations, iterator seek variants, multiget, and put-entity. `TraceUnit`, `TypeCorrelation`, and `StatsUnit` model individual accesses, correlation counters, and per-key aggregates. `TraceStats` owns per-CF aggregate counters, histograms, priority queues for top-k results, time-series queues, correlation output, whole/accessed-key maps, and many optional `WritableFile` handles. `TypeUnit` groups stats by operation type, while `CfUnit` stores CF-level whole/accessed key counts and QPS maps. `TraceAnalyzer` privately implements both `TraceRecord::Handler` and `WriteBatch::Handler`, exposing the high-level lifecycle `PrepareProcessing`, `StartProcessing`, `MakeStatistics`, `ReProcessing`, and `EndProcessing`.

## State, Persistence, Integration, Risks, And Test Signals

The header shows that analyzer state is mostly in-memory until explicitly flushed through `WritableFile` handles. It depends on RocksDB `Env`, `TraceReader`, `TraceRecord`, `WriteBatch`, and `trace_replay` declarations. Important integration points are the handler overrides for decoded trace records, write-batch callbacks for each write operation, and `trace_analyzer_tool(int argc, char** argv)`. Copying is disabled for the large stats structures to avoid accidental file-handle and queue duplication, while moves are allowed. Risks include enum/index drift because arrays are sized by `kTaTypeNum`, large maps for high-cardinality traces, and many output-file pointers that must be opened and closed consistently. Tests in `trace_analyzer_test.cc` exercise the lifecycle and file outputs rather than the header directly.
