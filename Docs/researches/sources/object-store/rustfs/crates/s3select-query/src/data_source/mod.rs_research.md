# sources/object-store/rustfs/crates/s3select-query/src/data_source/mod.rs

## Purpose
This module exposes data-source adapters used by the query engine.

## Important APIs, Types, And Functions
It declares `pub mod table_source;`, exporting `TableSourceAdapter`, `TableHandle`, and related table-source functionality.

## Control Flow
No local control flow exists. Consumers use this module path to build metadata table sources.

## State And Persistence Behavior
No local state or persistence.

## Dependencies And Integration Points
`metadata` depends on `data_source::table_source` to expose registered table providers to DataFusion's planner.

## Risks And Edge Cases
Additional data-source modules must be exported here.

## Test Signals
No local tests; table-source behavior is exercised by metadata/planner integration.
