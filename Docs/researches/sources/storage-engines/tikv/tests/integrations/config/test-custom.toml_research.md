# sources/storage-engines/tikv/tests/integrations/config/test-custom.toml

## sources/storage-engines/tikv/tests/integrations/config/test-custom.toml

Purpose: comprehensive non-default TiKV config fixture used to prove schema coverage, aliases, enum parsing, nested tables, readable units, and backward compatibility.

Important sections: root slow-log/panic/memory flags; `[log]`, `[log.file]`, readpools; `[server]` and labels; `[storage]`, max-ts, block-cache, flow-control, IO priorities; `[pd]`, `[metric]`; extensive `[raftstore]`; `[coprocessor]`; RocksDB/Titan DB and CF configs; raftdb and raft-engine; security/encryption; backup, log-backup, import, gc/auto-compaction, pessimistic-txn, cdc, resolved-ts, split, and resource-control.

Control flow and state: `test_serde_custom_tikv_config` builds the matching `TikvConfig`, loads this file, applies split optimization, and requires debug equality. It also serializes the loaded value and deserializes it again.

Dependencies and integration points: nearly every TiKV config module and several legacy names, including `pessimistic-txn.enabled`, numeric `wake-up-delay-duration`, `partitioned-raft-kv`, and nested `split.split-*` keys. Risks include fixture drift after config default changes, renamed fields, and unit parsing differences. Test signal is full-object equality plus round-trip stability.
