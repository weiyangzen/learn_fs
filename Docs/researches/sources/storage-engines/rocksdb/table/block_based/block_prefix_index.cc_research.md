## sources/storage-engines/rocksdb/table/block_based/block_prefix_index.cc

Purpose: implements a compact hash index mapping key prefixes to candidate data-block IDs. It accelerates prefix-based lookup by reading prefix metadata blocks and building an in-memory bucket table.

Important APIs/functions: local helpers hash prefixes and encode/decode bucket entries. `BlockPrefixIndex::Builder::Add()` records a prefix span. `Builder::Finish()` builds the bucket array and optional block-array buffer. `BlockPrefixIndex::Create()` decodes serialized prefix and prefix-meta slices. `GetBlocks()` transforms a lookup key to an internal prefix and returns candidate block IDs.

Control flow: `Create()` iterates over `prefix_meta`, reading varint triples `(prefix_size, entry_index, num_blocks)`, slicing the corresponding prefix bytes from `prefixes`, and adding them to the builder. `Finish()` uses roughly one bucket per prefix, groups records by hash bucket, merges connected spans within a bucket, counts block-array storage, and fills buckets either with `kNoneBlock`, a direct block ID, or an encoded pointer into `block_array_buffer_`. `GetBlocks()` hashes the lookup prefix and decodes the bucket representation.

State and persistence behavior: source persistence is the table’s hash-index prefix and metadata blocks. Runtime state is `num_buckets_`, `buckets_`, `num_block_array_buffer_entries_`, `block_array_buffer_`, and an `InternalKeySliceTransform` wrapping the prefix extractor. The destructor releases the two arrays.

Dependencies/integration points: depends on `SliceTransform`, internal-key prefix transformation, `Arena`, varint coding, and RocksDB hash. It integrates with block-based table readers that load hash-index metadata and pass `BlockPrefixIndex` into index/data iterators.

Risks: malformed metadata can cause corruption statuses; hash collisions intentionally broaden candidate block sets. Builder assumes records arrive in nondecreasing block order for span merging assertions. `GetBlocks()` returns internal pointers that remain valid only for the index lifetime.

Test signals: direct tests are not in this file set, but `block_based_table_reader_test.cc` includes `kHashSearch` parameterization and prefix extractors, while block/hash behavior is indirectly exercised through table reads and cache checks.
