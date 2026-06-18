<!-- BEGIN_FILE_RESEARCH: sources/storage-engines/rocksdb/table/plain/plain_table_index.cc -->
# sources/storage-engines/rocksdb/table/plain/plain_table_index.cc

Purpose: Implements the hash/binary-search index block used by plain table readers and builders.

Important APIs and functions: Implements `PlainTableIndex::InitFromRawData()`, `PlainTableIndex::GetOffset()`, `PlainTableIndexBuilder::IndexRecordList::AddRecord()`, `AddKeyPrefix()`, `Finish()`, `AllocateIndex()`, `BucketizeIndexes()`, `FillIndexes()`, and static block name `PlainTableIndexBuilder::kPlainTableIndexBlock`.

Control flow: The builder receives prefix hashes and file offsets in sorted data order. It records one offset per prefix and then every `index_sparseness_` keys within a prefix. `Finish()` selects hash table size from prefix count and `hash_table_ratio`, bucketizes records by `hash % index_size_`, computes subindex storage for collisions/multiple offsets, logs keys-per-prefix histogram, and serializes varint header, primary bucket array, and subindex offsets. The reader initializes raw pointers from persisted data and `GetOffset()` maps a prefix hash to empty, direct file offset, or subindex offset by inspecting the high flag bit.

State and persistence: Persisted index data contains varint index size, varint prefix count, an array of 32-bit bucket values, and subindex records. Empty buckets use `kMaxFileSize`; subindex pointers set `kSubIndexMask`. Runtime builder state includes record groups, prefix histogram, previous prefix/hash, sparseness counters, computed sizes, prefix extractor, and arena allocation.

Dependencies and integration points: Used by plain table builder and reader. Depends on `Arena`, immutable options logging, prefix extractor, hash utilities, coding helpers, unaligned fixed32 access, and histogram logging.

Risks: File offsets are limited to 31 bits. `InitFromRawData()` assumes enough bytes remain for the bucket array after reading varints. Collision subindex order is restored by reverse write from the per-bucket linked list. `hash_table_ratio <= 0` or no prefix extractor collapses to a single bucket and binary-search-heavy behavior.

Test signals: Empty/direct/subindex lookup behavior, collision-heavy buckets, index sparseness zero and nonzero, no-prefix-extractor fallback, large prefix counts, raw data round trips, max file size boundary, and reader binary search over subindex entries.
<!-- END_FILE_RESEARCH: sources/storage-engines/rocksdb/table/plain/plain_table_index.cc -->
