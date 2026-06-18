# sources/storage-engines/tikv/tests/benches/coprocessor_executors/util/executor_descriptor.rs

## Purpose
This module builds `tipb::Executor` protobuf descriptors used by DAG-based benchmarks.

## Important APIs, Types, and Functions
Functions include `table_scan`, `index_scan`, `selection`, `simple_aggregate`, `hash_aggregate`, `stream_aggregate`, and `top_n`. Each initializes a `PbExecutor`, sets the `ExecType`, and fills the relevant executor-specific protobuf fields.

## Control Flow
Descriptor builders clone column info and expression slices into protobuf repeated fields. `top_n` zips order expressions with direction flags into `ByItem`s and sets the limit.

## State and Persistence Behavior
No state is retained; descriptors are transient request metadata.

## Dependencies and Integration Points
It depends on `tipb` protobuf types and is used heavily by integrated, table scan, and index scan DAG benchmarks.

## Risks and Test Signals
Descriptor drift is the key risk: executor types, field names, or aggregation type conventions must remain aligned with TiDB/TiKV DAG handlers. Constructor compilation and DAG handler `unwrap()` failures catch regressions.
