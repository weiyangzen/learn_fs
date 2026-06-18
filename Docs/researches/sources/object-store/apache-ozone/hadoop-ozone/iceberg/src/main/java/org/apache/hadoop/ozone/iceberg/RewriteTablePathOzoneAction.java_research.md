# sources/object-store/apache-ozone/hadoop-ozone/iceberg/src/main/java/org/apache/hadoop/ozone/iceberg/RewriteTablePathOzoneAction.java

## Purpose
`RewriteTablePathOzoneAction` implements Iceberg's `RewriteTablePath` for Ozone-backed tables. It stages rewritten metadata JSON files, manifest lists, manifests, and position delete files while producing a CSV copy plan from staged paths to target paths.

## Important APIs, types, and functions
Fluent methods set source/target prefixes, start/end metadata versions, and staging location. `execute()` validates inputs, creates a fixed thread pool, runs `rebuildMetadata()`, and shuts down the pool. Major helpers include `validateVersion`, `rewriteVersionFiles`, `manifestsToRewrite`, `rewriteManifestLists`, `rewriteManifests`, `rewritePositionDeletes`, `positionDeletesReader`, and `positionDeletesWriter`.

## Control flow
Execution validates non-empty distinct prefixes, resolves end version to current metadata when omitted, validates optional start/end file names against current metadata logs and file existence, and defaults staging under the current metadata directory. It rewrites version metadata first using Iceberg `RewriteTablePathUtil.replacePaths`, computes delta snapshots, collects manifests from valid snapshots in bounded parallel batches, rewrites manifest lists and manifests, then rewrites referenced position-delete files.

## State and persistence behavior
State includes configured prefixes, version paths, staging dir, thread count, executor, and table reference. Persistent side effects are staged rewritten files and a `file-list` CSV in staging. The table is not committed by this action; the copy plan instructs a follow-up copy from staging to target.

## Dependencies and integration points
It depends heavily on Iceberg metadata, manifests, table operations, Avro/Parquet/ORC readers and writers, `RewriteTablePathUtil`, and `FileIO`. It integrates with `RewriteTablePathCommand` and Ozone/Hadoop table loading.

## Risks and edge cases
Partition statistics files are explicitly unsupported. Position delete rewriting can change file size after manifests have already been rewritten; the code documents this as a known Iceberg limitation that can affect catalogs using manifest file sizes. Thread count is not normalized, so zero or negative values can fail. Missing manifest lists produce a wrapped runtime failure advising an earlier version.

## Test signals
`TestRewriteTablePathOzoneAction` covers full and bounded version rewrites, default staging, missing/unknown/deleted versions, stats-file copy-plan validation, partition-stat rejection, missing manifest-list errors, unsupported formats, and AVRO/ORC/PARQUET position-delete round trips.
