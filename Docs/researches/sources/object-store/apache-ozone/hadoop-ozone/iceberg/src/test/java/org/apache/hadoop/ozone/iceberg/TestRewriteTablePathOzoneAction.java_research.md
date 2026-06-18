# sources/object-store/apache-ozone/hadoop-ozone/iceberg/src/test/java/org/apache/hadoop/ozone/iceberg/TestRewriteTablePathOzoneAction.java

## Purpose
`TestRewriteTablePathOzoneAction` validates the Iceberg path-rewrite CLI and action across full-table rewrites, version windows, validation failures, statistics handling, manifest-list failures, and position-delete IO formats.

## Important APIs, types, and functions
The suite uses `IcebergCommand`, `RewriteTablePathOzoneAction`, `RewriteTablePathOzoneUtils`, Iceberg `HadoopTables`, `TableMetadata`, `StaticTableOperations`, manifest readers, `DataFiles`, position delete writers/readers, and `RewriteTablePathUtil`. Helpers create a local table, read the generated CSV file-list, and assert internal paths in staged metadata and manifests.

## Control flow
Setup creates a temporary file-backed Iceberg table with four append commits and two row-delta commits containing position-delete files, then captures stdout/stderr. CLI tests run `rewrite-path` with source/target/staging and optional start/end/thread flags. Assertion helpers inspect staged metadata JSON, manifest lists, manifests, and staged delete files to verify paths now start with the target prefix while preserving expected file names.

## State and persistence behavior
Tests create real local Iceberg metadata, data-file metadata entries, delete files, staged rewritten artifacts, and file-list CSVs under JUnit temp directories. Table data files are represented by metadata entries except position delete files, which are physically written.

## Dependencies and integration points
The tests exercise Picocli command dispatch, Ozone configuration, Iceberg metadata operations, manifest AVRO IO, Parquet position delete IO, ORC/AVRO/PARQUET delete reader/writer round trips, and action error handling.

## Risks and edge cases
Covered risks include missing prefixes, identical source/target, unknown or deleted start/end metadata versions, unsupported partition statistics, missing manifest lists, unsupported file formats, and internal path rewrite completeness. The suite also documents the generated staging location contract.

## Test signals
Strong signals are exact copy-plan target sets, target-prefix assertions inside every staged artifact type, expected exception messages, successful command exit code, and position-delete row round-trip checks for supported formats.
