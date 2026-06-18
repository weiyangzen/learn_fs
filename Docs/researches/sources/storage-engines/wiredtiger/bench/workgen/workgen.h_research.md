# sources/storage-engines/wiredtiger/bench/workgen/workgen.h

## Purpose
`workgen.h` is the public C++ header for the workgen benchmark API and the contract exposed to Python by SWIG. It defines the user-visible model for creating tables, operations, threads, transactions, workloads, and for reading benchmark statistics.

## Important APIs, Types, and Functions
Key exported types are `OptionsList`, `Track`, `Stats`, `Context`, `TableOptions`, `Table`, `ParetoOptions`, `Key`, `Value`, `Operation`, `ThreadOptions`, `ThreadListWrapper`, `Thread`, `Transaction`, `WorkloadOptions`, and `Workload`. `Operation::OpType` covers checkpoint, insert, log flush, none/noop, remove, search, sleep, update, rollback-to-stable, and verify. Constructors encode common operation shapes: table-key-value operations, table-key operations, table-only operations, random-table operations, and config-string internal operations. `Workload::run(WT_CONNECTION *)` is the public execution entry point.

## Control Flow
Python scripts create `Context`, `Table`, `Operation`, and `Thread` objects, compose threads through SWIG-side operators backed by `ThreadListWrapper`, then construct `Workload` and call `run`. During execution, the private pointers declared here (`ContextInternal`, `TableInternal`, `OperationInternal`) are populated by `workgen.cpp` and drive actual WiredTiger calls. `Track` and `Stats` are both public data containers and runtime aggregation objects.

## State and Persistence Behavior
The public objects intentionally carry a mix of declarative and runtime state. `Table` has stable URI/options plus an internal table-id pointer. `Operation` can own config, key/value/table descriptions, transaction pointer, group pointer, dynamic table assignment vector, timing/repeat settings, and random-table behavior. `WorkloadOptions` includes persistent output names (`report_file`, `sample_file`) and runtime controls for timestamps, dynamic table creation/deletion, mirrored tables, background compaction, and latency sampling.

## Dependencies and Integration Points
The header is intentionally light: C++ STL containers and forward declarations keep it usable by SWIG. It integrates with `workgen.cpp` for implementation, `workgen_int.h` for private runtime state, WiredTiger through the `WT_CONNECTION *` parameter, and Python runner/helper code that relies on stable field names.

## Risks and Edge Cases
Because SWIG exposes fields directly, renaming or changing field types is API-breaking for benchmark scripts. Ownership is split: Python manages operation groups and transactions, while C++ manages internal pointers, so shallow copies are deliberate but risky. The header prevents assignment for `Track`/`Stats` except explicit methods, but many other copy operations preserve runtime pointers or internal IDs. Options must remain synchronized with `workgen.cpp` constructors and SWIG typemaps.

## Test Signals
SWIG build/import tests, Python examples in `bench/workgen/runner`, and workload composition tests are primary signals. API compatibility tests should instantiate every constructor shape, inspect help text, copy objects, and run a minimal workload against a temporary WiredTiger home.
