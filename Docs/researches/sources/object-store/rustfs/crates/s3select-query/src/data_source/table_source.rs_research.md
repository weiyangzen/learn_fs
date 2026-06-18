# sources/object-store/rustfs/crates/s3select-query/src/data_source/table_source.rs

## Purpose
This file adapts DataFusion `TableProvider` instances into planner-visible table sources with stable table names and logical plans.

## Important APIs, Types, And Functions
`TEMP_LOCATION_TABLE_NAME` is the synthetic name used for the current S3 object. `TableSourceAdapter::try_new` builds a logical scan plan from a table reference and provider. Accessors expose database name, table name, table handle, plan, schema, and filter pushdown. `TableHandle` wraps an `Arc<dyn TableProvider>`.

## Control Flow
`try_new` converts the provider to a `TableSource`. If the source exposes a logical plan, it uses that; otherwise it builds a scan through `LogicalPlanBuilder::scan`. Metadata providers later return the adapter as a `TableSource` to DataFusion SQL planning.

## State And Persistence Behavior
The adapter stores only in-memory provider handles and the derived logical plan. It does not persist metadata.

## Dependencies And Integration Points
It integrates DataFusion `TableProvider`, `TableSource`, `LogicalPlanBuilder`, filter pushdown, schemas, and table references. `MetadataProvider` uses it to resolve `S3Object` and aliases.

## Risks And Edge Cases
The database name is hard-coded to `default_db`. Filter pushdown relies on the underlying provider and may differ across CSV/JSON listing tables and parquet custom tables. Logical-plan caching means provider changes after adapter creation are not reflected.

## Test Signals
No direct tests. Planner and integration tests exercise it by resolving `S3Object` scans.
