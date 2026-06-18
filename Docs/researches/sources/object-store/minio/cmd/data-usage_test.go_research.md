<!-- BEGIN_FILE_RESEARCH: sources/object-store/minio/cmd/data-usage_test.go -->
## sources/object-store/minio/cmd/data-usage_test.go

Purpose: This hand-written test file validates scanner data usage cache updates, prefix compaction behavior, cache serialization/deserialization, and utility helpers for constructing test file trees.

Important APIs and functions: `usageTestFile` describes test file paths and sizes. `TestDataUsageUpdate` exercises `scanDataFolder` over a bucket rooted below a temporary xlStorage drive. `TestDataUsageUpdatePrefix` exercises scanning when paths include bucket prefixes and compaction thresholds. `TestDataUsageCacheSerialize` exercises `dataUsageCache.serializeTo` and `deserialize`. Helpers `createUsageTestFiles`, `generateUsageTestFiles`, and `equalAsJSON` support test setup and comparison.

Control flow: The update tests create a temporary directory tree, define a `getSize` callback that returns file size and one version for files, initialize `xlStorage.diskInfoCache`, and scan the bucket. They then call `find`, `flatten`, and compare expected size, object count, version count, and histograms for root and selected directories. The tests mutate the tree by adding files and deleting one file, run `scanDataFolder` for `dataUsageUpdateDirCycles`, increment `NextCycle`, and verify changed directories are reflected. Prefix tests also generate many small files to trigger compaction and check that deeply nested compacted entries are represented at expected parents. Serialization tests scan a richer tree, replace one entry, serialize to a buffer, deserialize into a new cache, verify `LastUpdate` is set and preserved, and compare each cache entry via JSON.

State and persistence behavior: All state is local to temporary directories and memory buffers, but it mirrors production cache lifecycle: scan from disk, update `dataUsageCache`, compact children, serialize to the binary cache format, and deserialize. The tests exercise cache mutation across scanner cycles, including adding and removing files.

Dependencies and integration points: The tests depend on scanner types (`scannerItem`, `sizeSummary`, `scanDataFolder`), `xlStorage`, `cachevalue`, `DiskInfo`, `dataUsageCache`, histogram methods, and filesystem functions. They integrate with production scanner code rather than mocking the entire scanner path.

Risks: The tests rely on production constants such as `dataUsageUpdateDirCycles`, `dataScannerCompactLeastObject`, and `dataScannerCompactAtFolders`; changes to compaction heuristics require expected values to be revisited. JSON comparison avoids Go map-order issues but can hide differences in unexported fields. The `getSize` callback models one version per file and does not cover delete markers, multipart metadata, tier stats, or healing behavior.

Test signals: This is the strongest listed test coverage for data usage cache behavior. It checks real filesystem traversal, incremental update detection, compaction, histograms, object/version counts, and binary serialization round-trip on populated cache data.
<!-- END_FILE_RESEARCH: sources/object-store/minio/cmd/data-usage_test.go -->
