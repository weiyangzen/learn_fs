# sources/object-store/rustfs/crates/s3select-query/src/metadata/base_table.rs

## Purpose
This file implements a simple table-handle provider for resolving a default table provider from a `TableHandle`.

## Important APIs, Types, And Functions
`BaseTableProvider` is a zero-field default struct implementing `TableHandleProvider`. `build_table_handle(Arc<dyn TableProvider>) -> DFResult<TableHandle>` wraps a provider in a `TableHandle`.

## Control Flow
The method wraps the passed provider without additional lookup or authorization logic.

## State And Persistence Behavior
The provider is stateless and performs no persistence.

## Dependencies And Integration Points
It depends on DataFusion `TableProvider` and local `TableHandle`. `MetadataProvider` uses this interface to turn table handles into planner sources.

## Risks And Edge Cases
This provider does not maintain a catalog, so all table resolution must already have produced a valid `TableHandle`. Any future multi-table support needs a richer provider.

## Test Signals
Covered indirectly by all planner tests that resolve `S3Object`.
