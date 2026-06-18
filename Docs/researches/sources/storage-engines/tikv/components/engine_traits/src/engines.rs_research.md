# sources/storage-engines/tikv/components/engine_traits/src/engines.rs

Purpose: Bundles the key-value and Raft engines used by a TiKV store.

Important APIs and control flow: `Engines<K, R>` stores `kv` and `raft` fields. Its constructor `new` returns the pair, and generic bounds require `K: KvEngine` and `R: RaftEngine`.

State, persistence, and dependencies: It is a lightweight owner/transport for two persistent engines; durability belongs to the contained engines.

Integration points, risks, and test signals: Used by store/bootstrap code that must pass both engines together. Risks are accidental cloning or lifecycle mismatch between KV and Raft engines. Signals are broad compile-time integration rather than local unit tests.
