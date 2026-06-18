# sources/storage-engines/tikv/components/test_coprocessor/src/dag.rs

## Purpose
This file provides builders for TiDB DAG coprocessor requests and a chunk splitter for decoding streaming/select results into rows of `Datum`. It lets tests express table scans, index scans, selections, projections, aggregations, ordering, limits, paging, and index lookup DAGs without hand-writing protobuf wiring.

## Important APIs, Types, And Functions
`DagSelect` stores the executor chain, output columns, order-by expressions, aggregate/group expressions, key ranges, output offsets, paging, start timestamp, and intermediate-output channels. `from(table)` creates a table-scan DAG over all records; `from_index(table, index)` creates an index scan. Builder methods add operators: `index_lookup`, `limit`, `order_by`, aggregate helpers (`count`, `sum`, `avg`, etc.), `group_by`, `where_expr`, `projection`, `desc`, `paging_size`, `key_ranges`, and `start_ts`.

`build_with` appends aggregation, TopN, and Limit executors as needed, sets flags, output offsets, intermediate channels, request type `REQ_TYPE_DAG`, serialized `DagRequest`, ranges, paging size, context, and start TS. `DagChunkSpliter` iterates over `tipb::Chunk`s, decodes row data into datums, and yields fixed column-count rows.

## Control Flow And State
`DagSelect` mutates in builder style, with executor order determined by call sequence plus final `build_with` append logic. `index_lookup` rewrites executor parents, inserts a table scan and `IndexLookUp` executor, and transfers output offsets through an `IntermediateOutputChannel`. `DagChunkSpliter::next` lazily removes chunks, decodes all datums for a chunk, then splits off row-sized groups.

## Integration Points
The module integrates `kvproto::coprocessor::Request`, `tipb` executors, TiDB datum encoding, table/key-range helpers, and the crate's `Table`, `Column`, and `offset_for_column`. It is used by tests that feed requests to a TiKV coprocessor `Endpoint`.

## Risks And Test Signals
Several paths unwrap protobuf serialization, datum decode, and number encoding. `desc` assumes the first executor is a table scan and will not work for index scans. `offset_for_column` returns zero when not found, so expression builders can silently target the first column if schema metadata is wrong. Chunk splitting removes from the front of a vector and asserts enough datums remain. Tests should validate both unary and streaming responses when using complex DAGs.
