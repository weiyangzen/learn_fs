# sources/storage-engines/tikv/tests/integrations/server/gc_worker.rs

Purpose: verifies GC bypasses Raft and directly removes obsolete MVCC data/write records from local engines in raftstore v1 and v2 clusters.

Important APIs and functions: parameterized `test_gc_bypass_raft`, `must_kv_prewrite`, `must_kv_commit`, `sync_gc`, `Key::append_ts`, `keys::data_key`, and direct `Peekable` reads from default CF and `CF_WRITE`.

Control flow: creates a two-node cluster, writes four committed versions of one key, confirms data and write records exist, then for each store runs `sync_gc` over a region range covering the key with safe point 200 and verifies older start/commit timestamp records are gone.

State and persistence: persists MVCC versions and validates local deletion from every store. Since GC bypasses Raft, each store's GC worker must clean its own engine.

Dependencies and integration: KV transaction helpers, raftstore simulation, GC worker scheduler, engine traits, MVCC key encoding.

Risks: hand-mutated region range must match key encoding; the test focuses on deletion of old versions and does not deeply assert newest-version preservation.

Test signals: old default and write CF records disappear on all stores for both raftstore implementations.
