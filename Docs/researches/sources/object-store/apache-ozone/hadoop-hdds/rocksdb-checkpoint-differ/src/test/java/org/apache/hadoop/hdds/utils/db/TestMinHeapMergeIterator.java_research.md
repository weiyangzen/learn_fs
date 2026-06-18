<!-- BEGIN_FILE_RESEARCH: sources/object-store/apache-ozone/hadoop-hdds/rocksdb-checkpoint-differ/src/test/java/org/apache/hadoop/hdds/utils/db/TestMinHeapMergeIterator.java -->
# sources/object-store/apache-ozone/hadoop-hdds/rocksdb-checkpoint-differ/src/test/java/org/apache/hadoop/hdds/utils/db/TestMinHeapMergeIterator.java

Purpose: Unit tests for generic min-heap merging and resource cleanup behavior in `MinHeapMergeIterator`.

Important APIs/types/functions: Defines `TrackingCloseableIterator` to count closes, `MergeResult` to record merged key and source indexes, and `TestIterator` as a concrete `MinHeapMergeIterator<byte[], TrackingCloseableIterator<byte[]>, MergeResult>` using unsigned byte lexicographic comparison.

Control flow and state: Tests create sorted iterator inputs, trigger lazy initialization via `hasNext`, consume outputs, inspect merged source sets, and verify close counts. Exception tests inject `IOException` or `RocksDatabaseException` from `getIterator` and assert wrapping in `UncheckedIOException` plus cleanup of already-opened iterators.

Dependencies and integration points: Validates the primitive used by `SstFileSetReader` for multi-SST key merging.

Risks: The tests intentionally close never-registered iterators manually in exception cases, confirming the production iterator can only clean registered resources. They do not test comparator inconsistency or unsorted input because those are caller contract violations.

Test signals: Strong coverage of sorted ordering, duplicate grouping across three sources, empty iterator close on init, idempotent close, initialization failure cleanup, and `NoSuchElementException` on empty iteration.
<!-- END_FILE_RESEARCH: sources/object-store/apache-ozone/hadoop-hdds/rocksdb-checkpoint-differ/src/test/java/org/apache/hadoop/hdds/utils/db/TestMinHeapMergeIterator.java -->
