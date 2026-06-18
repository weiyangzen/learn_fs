# sources/object-store/apache-ozone/hadoop-hdds/framework/src/main/java/org/apache/hadoop/hdds/utils/db/RDBTable.java

## Purpose

`RDBTable` is the byte-array table implementation over a single RocksDB column family. It is marked private and is intended to sit under `TypedTable`, which handles object codecs and cache semantics. The complete 331-line source was read for this report.

## Important APIs, Types, and Functions

The class implements `Table<byte[], byte[]>` and wraps a `RocksDatabase`, `RocksDatabase.ColumnFamily`, and `RDBMetrics`. It exposes `put`, `putWithBatch`, `isEmpty`, `isExist`, `get`, `getIfExist`, `delete`, `deleteRange`, `iterator`, `getEstimatedKeyCount`, `deleteBatchWithPrefix`, `dumpToFileWithPrefix`, `loadFromFile`, and `getRangeKVs`. Package-private overloads handle `ByteBuffer` and `CodecBuffer` fast paths.

## Control Flow

Most operations delegate directly to `RocksDatabase` with the table's column family. Existence checks use RocksDB `keyMayExist` first, record metrics, and fall back to `get` only when the result is inconclusive. Iteration creates byte-array or codec-buffer iterators with optional prefix and `IteratorType`. Range listing seeks either to the first key or a validated start key, filters keys, optionally stops at the first mismatch after results have begun when sequential listing is requested, and logs debug timing/filter counters.

## State and Persistence Behavior

Persistent data lives in RocksDB. Batched writes are recorded into `RDBBatchOperation` and persist only when the owning batch is committed. `dumpToFileWithPrefix` writes matching entries to an external SST file through `RDBSstFileWriter`; `loadFromFile` ingests it back into the column family. `deleteRange` and prefix batch deletion modify persistent key ranges.

## Dependencies and Integration Points

It depends on RocksDB wrapper classes (`RocksDatabase`, `RDBBatchOperation`, `RDBStoreByteArrayIterator`, `RDBStoreCodecBufferIterator`, `RDBSstFileWriter`, `RDBSstFileLoader`), `MetadataKeyFilters.KeyPrefixFilter`, `CodecBufferCodec`, and `RDBMetrics`. `TypedTable` is its main consumer.

## Risks and Edge Cases

Batch methods require `RDBBatchOperation` and throw on unexpected implementations. `keyMayExist` may be inconclusive, so tests must cover both definite and fallback paths. `getRangeKVs` rejects negative counts but permits zero-count empty results. Prefix buffers in `dumpToFileWithPrefix` must be closed on iterator creation failure. Start keys that do not exist return an empty range unless the key is compatible with a prefix edge case.

## Test Signals

Tests should cover metrics increments for get/existence paths, batch type validation, range scans with missing start keys, prefix filters, sequential stop behavior, SST dump/load round trips, direct-buffer get/delete paths, and iterator closure.
