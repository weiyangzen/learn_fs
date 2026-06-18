# sources/storage-engines/foundationdb/fdbclient/include/fdbclient/BulkLoading.h

Purpose: shared metadata, parsing, validation, and factory declarations for BulkLoad/BulkDump workflows.

Important APIs and types: defines verbosity helpers, path/key helpers, `BulkLoadType`, `BulkLoadTransportMethod`, manifest format version, `BulkLoadByteSampleSetting`, `BulkLoadChecksum`, `BulkLoadFileSet`, `BulkLoadManifest`, `BulkLoadManifestSet`, `BulkLoadTaskState`, `BulkLoadJobState`, job manifest header/entry types, `SSBulkLoadMetadata`, and factory/path functions such as `createBulkLoadTask`, `createBulkLoadJob`, `getBulkLoadJobRoot`, and sample filename generation.

Control flow: file sets validate root/manifest/data/sample relationships and produce full paths. Manifests serialize to a human-readable line format and parse back with strict field counts and version checks. Manifest sets aggregate compatible manifests, tracking min begin/max end and shared transport/load/sample settings. Task state starts submitted or complete for empty data, tracks data-move id, phase timings, restart count, and whether file ingestion is possible. Job state tracks global phase, root, range, submit/end times, counts, and errors.

State and persistence: these structs are serialized with file identifiers into system metadata and manifest files. Storage-server local metadata records data-move IDs for restart recovery when bulk loading without direct SST ingestion.

Dependencies and integration: includes Flow error/random/platform/trace utilities, `FDBTypes.h`, and knobs. Integrates with data distributor data moves, storage servers, blob/local file transport, backup BulkDump snapshots, and management APIs.

Risks: manifest parsing is fragile by design: comma-space splitting means field formatting is a compatibility contract. `BulkLoadManifest::isValid` requires non-empty range and valid byte sampling, so partially initialized job manifests are only valid in specific contexts. Phase transitions must coordinate with data movement.

Test signals: bulk load/dump simulation tests, manifest encode/decode tests, data move metadata tests, and backup BulkDump/BulkLoad restore tests.
