<!-- BEGIN_FILE_RESEARCH: sources/storage-engines/rocksdb/table/plain/plain_table_bloom.cc -->
# sources/storage-engines/rocksdb/table/plain/plain_table_bloom.cc

Purpose: Implements the legacy Bloom filter variant used by RocksDB plain table files for schema/backward compatibility.

Important APIs and functions: Implements `PlainTableBloomV1` construction, `SetRawData()`, `SetTotalBits()`, `BloomBlockBuilder::AddKeysHashes()`, `BloomBlockBuilder::Finish()`, and the `BloomBlockBuilder::kBloomBlock` meta block name.

Control flow: `SetTotalBits()` rounds requested bits either to a byte boundary or to a whole odd number of cache-line-sized locality blocks, allocates aligned memory from an `Allocator`, zeroes it, and adjusts the data pointer to cache-line alignment when locality is enabled. `AddKeysHashes()` inserts each precomputed hash into the embedded Bloom structure. `Finish()` exposes the raw Bloom bytes for writing to the table file.

State and persistence: The Bloom bit array is allocated in the provided allocator/arena and persisted as the plain table Bloom meta block when the builder stores indexes in the file. `SetRawData()` points a Bloom object at bytes read from an existing table.

Dependencies and integration points: Depends on `Allocator`, `LegacyLocalityBloomImpl`, `LegacyNoLocalityBloomImpl`, cache line constants, and plain table builder/reader meta block handling. The block name is added to the metaindex by `PlainTableBuilder`.

Risks: This is a legacy format and should not be reused for new filter applications. Alignment shifts mean the original allocated pointer and `data_` can differ, so lifetime belongs to the allocator. False-positive behavior depends on `num_probes`, total bit rounding, and whether prefix or full-key hashes are inserted by the caller.

Test signals: Locality and non-locality Bloom creation, raw data restoration, hash add/may-contain consistency, cache-line-aligned allocation paths, huge page allocator paths, and plain table read/write compatibility with existing Bloom version metadata.
<!-- END_FILE_RESEARCH: sources/storage-engines/rocksdb/table/plain/plain_table_bloom.cc -->
