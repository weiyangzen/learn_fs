<!-- BEGIN_FILE_RESEARCH: sources/object-store/apache-ozone/hadoop-hdds/rocksdb-checkpoint-differ/src/main/java/org/apache/hadoop/hdds/utils/db/MinHeapMergeIterator.java -->
# sources/object-store/apache-ozone/hadoop-hdds/rocksdb-checkpoint-differ/src/main/java/org/apache/hadoop/hdds/utils/db/MinHeapMergeIterator.java

Purpose: Generic closable merge iterator that combines multiple already-sorted closeable iterators into sorted groups using a priority queue.

Important APIs/types/functions: Type parameters are key `K`, iterator `I extends Iterator<K> & Closeable`, and output `V`. Subclasses implement `getIterator(int)` and `merge(Map<Integer,K>)`. `hasNext` lazily initializes all iterators and heap entries. `next` polls every heap entry whose current key compares equal and passes the per-source key map to `merge`. `HeapEntry` stores iterator index, current key, and comparator.

Control flow and state: Initialization creates and stores one iterator per index, advances each once, and closes empty iterators. If initialization throws, already-opened iterators are closed. During iteration, exhausted iterators are closed immediately. `close` closes all registered iterators and wraps the last `IOException` in `UncheckedIOException`.

Dependencies and integration points: Used by `SstFileSetReader.MultipleSstFileIterator` to merge keys across SST files and suppress duplicates. Its comparator determines ordering and grouping semantics.

Risks: `HeapEntry.equals` and `hashCode` are based on current key rather than iterator identity; this is acceptable for priority queue use but would be risky in hash collections. Duplicate grouping requires all source iterators to be sorted under the same comparator. Only the last close exception is retained.

Test signals: `TestMinHeapMergeIterator` covers sorted merge order, duplicate source grouping, empty iterator closure, idempotent close, initialization exception cleanup, and no-element behavior.
<!-- END_FILE_RESEARCH: sources/object-store/apache-ozone/hadoop-hdds/rocksdb-checkpoint-differ/src/main/java/org/apache/hadoop/hdds/utils/db/MinHeapMergeIterator.java -->
