# sources/storage-engines/rocksdb/java/src/test/java/org/rocksdb/CompactionOptionsUniversalTest.java

## Purpose

Accessor coverage for universal compaction configuration.

## Important APIs, control flow, and dependencies

The tests create `CompactionOptionsUniversal` and round-trip `sizeRatio`, `minMergeWidth`, `maxMergeWidth`, `maxSizeAmplificationPercent`, `compressionSizePercent`, `stopStyle`, and `allowTrivialMove`.

## State, persistence, risks, and test signals

Only native option storage is involved. Risks include enum mapping for `CompactionStopStyle`, integer conversion, and boolean default drift. Signals are exact getter equality after each setter.
