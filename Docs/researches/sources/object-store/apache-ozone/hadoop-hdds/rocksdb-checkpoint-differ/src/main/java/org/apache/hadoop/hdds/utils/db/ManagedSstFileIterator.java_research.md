<!-- BEGIN_FILE_RESEARCH: sources/object-store/apache-ozone/hadoop-hdds/rocksdb-checkpoint-differ/src/main/java/org/apache/hadoop/hdds/utils/db/ManagedSstFileIterator.java -->
# sources/object-store/apache-ozone/hadoop-hdds/rocksdb-checkpoint-differ/src/main/java/org/apache/hadoop/hdds/utils/db/ManagedSstFileIterator.java

Purpose: Package-private abstract iterator that wraps RocksDB `SstFileReader` iteration in HDDS managed-resource types and exposes a `ClosableIterator<T>` contract.

Important APIs/types/functions: The constructor opens a `ManagedSstFileReader`, creates a `ManagedSstFileReaderIterator`, seeks to first, stores an `IteratorType`, and initializes reusable key/value `Buffer` instances backed by `CodecBuffer` capacity hints. `getIteratorValue(CodecBuffer key, CodecBuffer value)` is abstract and lets callers decode only the requested fields. `hasNext`, `next`, and `close` implement iteration and cleanup.

Control flow and state: `hasNext` delegates to RocksDB iterator validity. `next` reads key/value buffers only when the `IteratorType` requests them, calls subclass decoding, then advances the RocksDB iterator. `close` is synchronized and idempotently closes the iterator and reader and releases buffers.

Dependencies and integration points: Used by `SstFileSetReader.getKeyStream` to read regular SST keys without tombstones. Depends on managed RocksDB reader/read options, `Buffer`, `CodecBuffer`, `IteratorType`, and Ozone `ClosableIterator`.

Risks: `next` does not check `hasNext`; callers should obey iterator protocol. Resource safety depends on consumers closing the iterator, though higher-level merge iterators close exhausted iterators. Buffer lifetime is shared per iterator, so decoded values should not hold mutable buffer references beyond the call unless copied.

Test signals: Covered through `TestSstFileSetReader` regular key stream cases and merge iterator cleanup tests.
<!-- END_FILE_RESEARCH: sources/object-store/apache-ozone/hadoop-hdds/rocksdb-checkpoint-differ/src/main/java/org/apache/hadoop/hdds/utils/db/ManagedSstFileIterator.java -->
