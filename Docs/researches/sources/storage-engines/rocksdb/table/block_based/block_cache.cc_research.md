## sources/storage-engines/rocksdb/table/block_based/block_cache.cc

Purpose: implements typed block-cache creation and helper lookup for block-based table blocks. It bridges raw cached block contents to strongly typed block-like wrappers and selects cache item helpers based on `BlockType` and cache tier.

Important APIs/functions: `BlockCreateContext::Create()` overloads build `Block_kData`, `Block_kIndex`, `Block_kFilterPartitionIndex`, `Block_kRangeDeletion`, `Block_kMetaIndex`, `Block_kUserDefinedIndex`, `ParsedFullFilterBlock`, and `DecompressorDict`. `GetCacheItemHelper()` returns either full helper support for secondary cache/non-volatile tiers or basic helper support for volatile-only use.

Control flow: typed cache code passes raw or decompressed `BlockContents` into `BlockCreateContext`. Data/index/meta variants allocate a `Block` wrapper with appropriate read-amplification and restart interval metadata, then initialize per-KV protection information according to block role. Filter and decompressor dictionary variants construct non-`Block` parsed objects. Helper arrays are indexed by `BlockType` enum values and intentionally leave unsupported block types as `nullptr`.

State and persistence behavior: no disk persistence is introduced here. Runtime state comes from `BlockCreateContext` fields such as table options, immutable options, statistics, decompressor, comparator, checksum bytes per key, index value flags, and restart intervals. Cache helper selection controls how cached entries are charged, serialized, and used with secondary cache.

Dependencies/integration points: depends on `block_cache.h`, `BlockBasedTableReader`, typed cache APIs, `ParsedFullFilterBlock`, decompression utilities, and `BlockType` ordering. Block readers rely on these wrappers to initialize checksum verification and memory accounting consistently.

Risks: helper arrays must stay aligned with `BlockType`; adding an enum value without updating arrays can produce wrong helper lookup. Context pointers such as `table_options`, `ioptions`, and `decompressor` must be valid when compression or parsing needs them. Meta-index blocks are constructible but not stored in block cache.

Test signals: checksum initialization and approximate memory tests in `block_test.cc` use `BlockCreateContext`; reader tests cover cache insertion, secondary cache style typed helpers indirectly, and strict cache capacity behavior.
