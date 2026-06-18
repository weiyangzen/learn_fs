# sources/storage-engines/rocksdb/java/src/main/java/org/rocksdb/LevelMetaData.java research

## Purpose

`LevelMetaData` is a Java snapshot of native RocksDB metadata for one LSM level. It is returned by metadata APIs to describe level number, total file bytes, and the SST files in that level.

## Important APIs and types

The private constructor is called from JNI with `level`, `size`, and an array of `SstFileMetaData`. Public accessors are `level()`, `size()`, and `files()`, which returns `Arrays.asList(files)`.

## Control flow

Native code constructs the object. Java callers then read the immutable fields. No Java logic refreshes the metadata; callers must request a new metadata object to observe DB changes.

## State and persistence behavior

The class stores a point-in-time Java copy of metadata. It does not own files or native handles. `size` reflects persistent SST file sizes at collection time; compaction, flush, or deletion can make it stale.

## Dependencies and integration points

It depends on `SstFileMetaData` and is typically nested under `ColumnFamilyMetaData` or related RocksDB metadata APIs. It provides Java visibility into compaction layout and storage usage.

## Risks and test signals

`files()` exposes a fixed-size list backed by the internal array, so callers cannot add/remove but can observe mutable `SstFileMetaData` objects if those objects expose mutable internals. Tests should cover JNI construction, correct level aggregation, empty levels, and staleness expectations after compaction.
