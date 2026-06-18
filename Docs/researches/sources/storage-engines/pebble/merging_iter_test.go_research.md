# sources/storage-engines/pebble/merging_iter_test.go

## Purpose
`merging_iter_test.go` provides the main coverage for the legacy merging iterator. It combines generic iterator conformance, datadriven fake-iterator tests, table-backed range deletion tests, and benchmarks that model LSM fan-in, sequential seeks, bounds changes, prefix seeks, and long keys.

## Important APIs, types, and functions
Tests include `TestMergingIter`, `TestMergingIterSeek`, `TestMergingIterNextPrev`, and `TestMergingIterDataDriven`. Helpers include `buildMergingIterTables`, `buildLevelsForMergingIterSeqSeek`, and `buildMergingIter`. Benchmarks include `BenchmarkMergingIterSeekGE`, `BenchmarkMergingIterNext`, `BenchmarkMergingIterPrev`, `BenchmarkMergingIterSeqSeekGEWithBounds`, `BenchmarkMergingIterSeqSeekPrefixGE`, and `BenchmarkMergingIterSeekAndNextWithDominantL6AndLongKey`.

## Control flow and state behavior
The generic tests split sorted key/value data across multiple fake iterators and check merged behavior. Datadriven seek tests parse text fixtures into `base.FakeIter` children. The table-backed datadriven test builds in-memory sstables, writes point keys and fragmented range tombstones, constructs a `manifest.Version`, wires `levelIter` objects into `mergingIterLevel`, and runs internal iterator commands while optionally attaching point and range-deletion probes.

Benchmark helpers create real sstable readers on `vfs.NewMem`, often with cache handles, bloom filters, two-level indexes, range tombstones, and multi-level slices. The sequential seek benchmarks repeatedly update bounds or prefix seek forward, targeting the `TrySeekUsingNext` and file-locality paths used by CockroachDB scans.

## Dependencies and integration points
The file exercises integration with `sstable.Reader`, `RawWriter`, `levelIter`, `manifest.LevelSlice`, `keyspan.Fragmenter`, bloom filters, cache handles, `itertest`, datadriven fixtures under `testdata/merging_iter*`, and `testkeys.Comparer`. It also verifies `SetContext` on the iterator path.

## Risks and test signals
This is the strongest signal for legacy iterator correctness because it uses real table readers and range deletion iterators. Important risk areas are range tombstone truncation to table bounds, sentinel boundary keys, seek optimization safety, bounds reuse, and reverse iteration. Benchmarks are not correctness checks, but they document expected workload shapes and performance-sensitive paths.
