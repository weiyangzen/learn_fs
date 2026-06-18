## sources/storage-engines/pebble/sstable/block/category_stats.go

Purpose: Implements read-category registration, QoS tagging, and sharded block read statistics aggregation for iterator/file-cache usage.

Important APIs/types/functions: `Category`, `CategoryUnknown`, `CategoryMax`, `RegisterCategory`, `Categories`, `StringToCategoryForTesting`, `QoSLevel`, `CategoryStats`, `CategoryStatsShard`, `CategoryStatsCollector`, `Accumulator`, and `GetStats`. `CategoryStats` tracks block bytes, block bytes served from cache, and uncached read duration. `CategoryStatsAggregate` returns category-labeled totals.

Control flow: Categories are registered during initialization; after `Categories` is called, later registration panics because `categoriesList` is frozen. The collector lazily creates a `shardedCategoryStats` per category in a `sync.Map`, protected by a mutex around `LoadOrStore`. `Accumulator` hashes a caller-provided pointer-ish value through an LCG formula to select a shard. `GetStats` locks every shard, aggregates counters, and sorts by category.

State and persistence behavior: All state is process-local metrics. Category IDs are bounded by `CategoryMax`; category 0 is `unknown` and latency-sensitive. Shards are padded to reduce false sharing.

Dependencies and integration points: Used through `block.ReadEnv.IterStats` and file-cache category stats collectors. Depends on `sync`, `atomic`, `runtime.GOMAXPROCS`, `cmp/slices`, `time`, `unsafe`, `errors`, and `redact`.

Risks: Registration order assigns numeric category IDs, so all categories must be registered before readers call `Categories`. The `shardPadding` compile-time expression depends on `CategoryStatsShard` size staying below 64 bytes. Stats can over-count duration when concurrent readers wait on one physical read, as documented.

Test signals: No direct tests in this subset. Indirect coverage comes from iterator stats and category integration tests elsewhere.
