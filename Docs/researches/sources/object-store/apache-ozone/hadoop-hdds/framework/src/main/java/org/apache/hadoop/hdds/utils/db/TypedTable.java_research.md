# sources/object-store/apache-ozone/hadoop-hdds/framework/src/main/java/org/apache/hadoop/hdds/utils/db/TypedTable.java

## Purpose

`TypedTable<KEY,VALUE>` is the public typed metadata table implementation over `RDBTable`. It converts keys and values with `Codec`s, optionally uses direct `CodecBuffer` fast paths, and mediates table cache behavior. The complete 634-line source was read for this report.

## Important APIs, Types, and Functions

It implements all `Table` methods plus cache APIs. Important fields are `rawTable`, `keyCodec`, `valueCodec`, `supportCodecBuffer`, reusable buffer capacity, and `TableCache`. It has nested `TypedTableIterator` and abstract `RawIterator<RAW>`. Important private helpers include encode/decode methods, direct-buffer `getFromTable`, `getFromTableIfExist`, and iterator construction.

## Control Flow

Construction chooses `FullTableCache`, `PartialTableCache`, or `TableNoCache`; full cache is populated by iterating the whole raw table with epoch `-1`. Reads first consult cache: `EXISTS` returns a copied value for `get`/`getIfExist`, `NOT_EXIST` returns null, and `MAY_EXIST` falls through to RocksDB. Direct-buffer reads allocate a resizable output buffer, retry when RocksDB reports a larger required size, and decode from `CodecBuffer`. Writes and deletes use direct buffers when both codecs support them; batch direct buffers are intentionally handed to the batch for release after commit. Iterators wrap raw byte-array or codec-buffer iterators and decode entries lazily.

## State and Persistence Behavior

Persistent state lives in `RDBTable`/RocksDB. In-memory state lives in `TableCache`, where entries can represent values or tombstones with epochs. `cleanupCache` delegates to the cache implementation. `dumpToFileWithPrefix` and `loadFromFile` expose RocksDB SST import/export through typed prefixes.

## Dependencies and Integration Points

It depends on `Codec`, `CodecBuffer`, `RDBTable`, cache classes, `TableCacheMetrics`, `MetadataKeyFilters`, Ratis `Preconditions`, and `CheckedBiFunction`. It is the standard typed API exposed by DB store builders to OM/SCM/HDDS metadata code.

## Risks and Edge Cases

Cache semantics differ by cache type: full cache treats a miss as definitive, partial/no cache require DB lookup. `getReadCopy` returns the cached object reference and requires caller synchronization. Direct-buffer batch paths must release buffers on error but not after successful batch enqueue. Buffer resizing assumes required size remains stable between retries. Full-cache construction can be expensive for large tables.

## Test Signals

Tests should cover all cache types, tombstones, copy versus read-copy semantics, full-cache initial load, codec-buffer and byte-array paths, buffer resizing for large values, batch ownership on success/failure, range decoding, prefix delete/export/import, and iterator close/seek/remove behavior.
