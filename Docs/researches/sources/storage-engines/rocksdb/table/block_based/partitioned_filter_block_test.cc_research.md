# sources/storage-engines/rocksdb/table/block_based/partitioned_filter_block_test.cc

Purpose: unit tests for partitioned filter construction and lookup behavior, including historical prefix-partition bugs and user-defined timestamp compatibility.

Important APIs/types/functions: the file defines a global `blooms` map to simulate partition block storage, `MockedBlockBasedTable` to initialize required `Rep` fields from `PartitionedIndexBuilder`, and `MyPartitionedFilterBlockReader` to prepopulate `filter_map_` with `ParsedFullFilterBlock` objects. `PartitionedFilterBlockTest` creates builders/readers, writes returned filter partitions to the map, and verifies `KeyMayMatch`/`PrefixMayMatch`.

Control flow: helpers prepare timestamp-adjusted keys, estimate max index/filter sizes, build partitioned index/filter builders, repeatedly call `Finish` until not incomplete, and construct a reader over the final top-level index block. Tests vary metadata block size to force one, two, per-key, or all-key partitions.

State and persistence: tests do not write real SST files. They mimic persisted filter partition blocks with offsets in `blooms`, while the top-level filter index is put in an in-memory `Block`. This isolates filter logic from file IO but still exercises handle encoding and index iteration.

Dependencies/integration: uses Bloom filter policy internals, partitioned index builder, block-based table `Rep`, internal key and timestamp helpers, fixed prefix transforms, and RocksDB test harness parameterization.

Risks and test signals: coverage is meaningful across format versions `{2,3,4,5,default,latest}`, all user-defined timestamp modes, and both `decouple_partitioned_filters` booleans. It explicitly guards same-prefix-across-blocks and prefix-in-wrong-partition regressions. Gaps include real block cache insertion failures, prefetch/cache dependency paths, read-error fallback, and multiget partition grouping.
