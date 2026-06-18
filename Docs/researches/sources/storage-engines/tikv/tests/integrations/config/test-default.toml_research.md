# sources/storage-engines/tikv/tests/integrations/config/test-default.toml

## sources/storage-engines/tikv/tests/integrations/config/test-default.toml

Purpose: section-only default fixture ensuring an explicit but empty TOML layout deserializes exactly to `TikvConfig::default()`.

Important sections: empty `[log]`, `[log.file]`, `[memory]`, readpool sections, `[server]`, `[storage]`, `[storage.block-cache]`, `[pd]`, `[metric]`, `[raftstore]`, `[coprocessor]`, RocksDB/Titan/CF tables, `[raftdb]`, `[raftdb.defaultcf]`, `[raft-engine]`, `[security]`, `[import]`, and `[gc]`.

Control flow and state: `test_serde_default_config` compares both empty string TOML and this fixture to defaults. It has no runtime state or persistence beyond fixture reading.

Dependencies and integration points: serde default handling for optional nested config tables. Risk is adding a required table or changing table defaults without updating default construction. Test signal is exact `TikvConfig` equality.
