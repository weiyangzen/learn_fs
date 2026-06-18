# sources/storage-engines/tikv/tests/integrations/config/test-cache-compatible.toml

## sources/storage-engines/tikv/tests/integrations/config/test-cache-compatible.toml

Purpose: fixture for backward-compatible block cache migration from legacy per-CF cache fields to shared `storage.block-cache.capacity`.

Important fields: empty standard config tables plus `rocksdb.defaultcf.block-cache-size = "1GB"`, `rocksdb.writecf.block-cache-size = "1GB"`, `rocksdb.lockcf.block-cache-size = "128MB"`, and `raftdb.defaultcf.block-cache-size = "128MB"`.

Control flow and state: consumed by `test_block_cache_backward_compatible`, which deserializes it, observes no shared capacity before compatibility adjustment, then calls `compatible_adjust(None)` and checks the shared capacity equals the sum of the four legacy cache sizes.

Dependencies and integration points: TiKV config serde and compatibility adjustment. Risk is legacy fields being removed or no longer participating in capacity synthesis. Test signal is exact summed capacity.
