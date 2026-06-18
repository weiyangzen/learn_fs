# sources/storage-engines/pebble/level_iter_v2_rand_test.go

Purpose: this randomized test stress-checks `levelIterV2` against the generic `iterv2.CheckIter` model over many generated point/range-delete layouts split across random SSTable boundaries.

Important APIs/types/functions: `TestLevelIterV2Rand` runs 200 random seeds. `runLevelIterV2RandomTest` generates keys/spans, builds SSTables, creates the level iterator, constructs expected model data, and invokes `iterv2.CheckIter`. Helper functions `pickFileBoundaries`, `filterPointKeys`, `clipSpans`, and `createSSTable` create realistic per-file data and metadata.

Control flow: a random key config creates 50 point keys and 10 spans. Span keys are deduplicated by trailer to satisfy SSTable writer constraints. Random boundaries partition the keyspace; points are filtered and spans clipped into each file's half-open range. Empty partitions are skipped. The test opens real SSTable readers, defines a `newIters` callback for point and range-deletion iterators, optionally applies coarse bounds, and compares `levelIterV2` against expected points plus real range deletions plus synthetic file-boundary spans.

State and persistence behavior: all files are written to an in-memory filesystem and readers are closed on exit. The random seed, key config, bounds, file metadata, points, and spans are logged on failure for reproduction. No durable state is changed.

Dependencies and integration points: relies on `iterv2` random data/model checking, `manifest.LevelSlice`, raw SSTable writer/reader APIs, object storage wrappers, range-deletion fragment transforms, and test-key comparers. It tests `levelIterV2` with real SSTable iterators rather than only fake iterators.

Risks and test signals: randomized coverage is especially useful for edge cases around clipped spans, empty gaps, file-boundary spans, lower/upper bounds, and mixed operations. Because it uses random seeds, failures need the logged seed to reproduce. It intentionally models file boundaries as zero-length spans so expected output matches the iterator's synthetic boundary behavior.
