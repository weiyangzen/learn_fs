# sources/object-store/rustfs/crates/s3select-query/src/dispatcher/parquet_table.rs

## Purpose
This file implements a custom DataFusion `TableProvider` for a single parquet S3 Select object. It reads parquet metadata from the registered object store, exposes the file schema, and applies S3 Select scan ranges as parquet row-group access plans.

## Important APIs, Types, And Functions
`ParquetSelectTable` stores schema, object-store URL, object path, object size, and optional `ParquetAccessPlan`. `try_new` locates the object store, reads metadata with `ParquetObjectReader`, computes scan-range access, and constructs the provider. The `TableProvider` implementation returns `Base` table type, schema, exact filter pushdown, and a `DataSourceExec` built from `FileScanConfigBuilder` and `ParquetSource`. Helpers include `parquet_access_plan`, `access_plan_for_scan_range`, `row_group_start_offset`, and `non_negative_offset`.

## Control Flow
Construction parses `s3://bucket/key`, fetches object metadata, reads parquet footer metadata, computes a scan range from S3 bounds and object size, then builds an access plan that skips row groups whose starting byte offset falls outside the inclusive range. During scan, it creates one `PartitionedFile` with file size and parquet source, attaching the access plan when present.

## State And Persistence Behavior
The table provider is immutable and in memory. It reads object metadata and parquet footer data but does not persist anything.

## Dependencies And Integration Points
It integrates DataFusion catalog/session, object-store registry, parquet async reader, physical file scan config, `ParquetAccessPlan`, and API scan-range validation from `object_store.rs`. It is selected by `SimpleQueryDispatcher` when input serialization is parquet.

## Risks And Edge Cases
Row-group filtering is based on row-group start offset only, so row groups that overlap a range but start before it are skipped. Row groups with negative or missing file offsets are excluded. Scan-range validation errors are mapped into query store errors. Projection, limit, and filter pushdown rely on DataFusion after the file source is built.

## Test Signals
Inline tests cover access-plan construction and row-group offset handling. Integration tests verify parquet simple select, a tiny scan range returning zero rows, and a larger range returning all fixture rows.
