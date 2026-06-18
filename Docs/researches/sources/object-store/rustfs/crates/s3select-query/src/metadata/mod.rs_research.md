# sources/object-store/rustfs/crates/s3select-query/src/metadata/mod.rs

## Purpose
This file implements the DataFusion `ContextProvider` used by SQL planning. It resolves S3 Select table references, function metadata, variables, and session configuration.

## Important APIs, Types, And Functions
`ContextProviderExtension` extends DataFusion `ContextProvider` with async `get_table_source`. `TableHandleProvider` abstracts table-provider retrieval. `MetadataProvider` stores the current object provider, a table-handle provider, a function manager, and session. `new` constructs it. Context-provider methods include table source lookup, function lookup, aggregate/window lookup, variable type resolution, options, and UDF listing.

## Control Flow
When the planner asks for a table, `get_table_source` checks for `S3Object`/temporary table references and builds a `TableSourceAdapter` around the current object provider. Function methods delegate to `FunctionMetadataManager`. Variable and config methods defer to DataFusion session/config behavior where supported.

## State And Persistence Behavior
The provider is per logical-planning operation and holds in-memory Arcs. It does not persist metadata or query state.

## Dependencies And Integration Points
It integrates DataFusion SQL planner traits, table-provider adapters, `BaseTableProvider`, `FuncMetaManagerRef`, DataFusion variable types, and API `SessionCtx`. It is built by `SimpleQueryDispatcher`.

## Risks And Edge Cases
Only the current S3 object table is supported. System variable handling is minimal. Table-reference matching must handle aliases and exact names consistently with `SqlPlanner`. Function lookup errors propagate through DataFusion planning.

## Test Signals
Integration tests exercise table resolution for `S3Object`, aliases, filters, order, grouping, JSON, CSV, and parquet.
