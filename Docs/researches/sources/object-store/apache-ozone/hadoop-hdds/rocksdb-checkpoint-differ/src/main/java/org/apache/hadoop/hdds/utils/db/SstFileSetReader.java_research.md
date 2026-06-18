<!-- BEGIN_FILE_RESEARCH: sources/object-store/apache-ozone/hadoop-hdds/rocksdb-checkpoint-differ/src/main/java/org/apache/hadoop/hdds/utils/db/SstFileSetReader.java -->
# sources/object-store/apache-ozone/hadoop-hdds/rocksdb-checkpoint-differ/src/main/java/org/apache/hadoop/hdds/utils/db/SstFileSetReader.java

Purpose: High-level reader for a collection of SST files that exposes merged key streams and estimated key counts across files.

Important APIs/types/functions: `getEstimatedTotalKeys()` sums RocksDB table property entry counts and caches the result. `getKeyStream(lower, upper)` reads regular keys through `ManagedSstFileIterator` and managed `ReadOptions` bounds. `getKeyStreamWithTombstone(lower, upper)` uses native `ManagedRawSSTFileReader` and raw iterator so delete records are included. Nested `MultipleSstFileIterator<T>` extends `MinHeapMergeIterator` and returns one representative value per merged duplicate key.

Control flow and state: Estimated count is lazily computed with double-checked synchronization. Key stream constructors create per-stream options and optional lower/upper `ManagedSlice`s, then lazily open per-file iterators during heap initialization. Close releases iterators, options, read options, and slices.

Dependencies and integration points: This class bridges snapshot diff SST file lists to key iteration. It depends on string codecs, managed RocksDB SST readers, raw native reader support for tombstones, and `MinHeapMergeIterator`.

Risks: Duplicate merge returns an arbitrary value from equal keys because `merge` uses `findAny`; this is fine for key-only streams but would not preserve newest-file value semantics. Native tombstone mode requires optional native library availability. Bounds must be encoded consistently with SST key encoding.

Test signals: `TestSstFileSetReader` covers zero/multiple file counts, lower/upper bounds, tombstone-including native mode, overlapping SST files, duplicate suppression, sorted output, and large binary-ish key prefixes.
<!-- END_FILE_RESEARCH: sources/object-store/apache-ozone/hadoop-hdds/rocksdb-checkpoint-differ/src/main/java/org/apache/hadoop/hdds/utils/db/SstFileSetReader.java -->
