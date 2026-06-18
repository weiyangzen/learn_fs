# sources/storage-engines/wiredtiger/test/suite/test_layered_config02.py

Purpose: intended to test disaggregated storage with block cache, especially long delta chains and cached page reuse, but currently skips in `early_setup` due to FIXME-WT-15663.

Important APIs/types/functions: when enabled, it would use block cache config `block_cache=(enabled=true,type="dram",size=256MB)`, `stat.conn.block_cache_blocks_removed`, `cache_read_leaf`, `cache_pages_requested_leaf`, debug eviction `debug=(release_evict)`, timestamped checkpoints, and scenarios for `layered:` and shared `table:` prefixes.

Control flow: skipped before execution. The dormant body creates a table, writes 500 rows, checkpoints, records block-cache removal stats, repeatedly updates one key across 10 checkpoints to build deltas, evicts and rereads the key, evicts again, verifies block-cache removal increased, then rereads while checking leaf reads do not increase but page requests do.

State and persistence behavior: persistent state would be checkpointed deltas and block-cache contents after eviction/reload. The expected behavior is that rereads can be satisfied from block cache.

Dependencies/integration points: block cache, disaggregated page reads, eviction, layered/shared table creation, stats.

Risks: currently no behavioral signal because it is skipped. If re-enabled, stat expectations may be sensitive to cache implementation and eviction timing.

Test signals: active signal is only the skip. Future pass would prove block cache integration with disaggregated pages and delta chains.
