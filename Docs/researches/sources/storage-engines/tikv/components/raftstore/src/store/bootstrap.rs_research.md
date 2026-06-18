# sources/storage-engines/tikv/components/raftstore/src/store/bootstrap.rs

Purpose: Provides helpers for initializing a raftstore store and preparing or clearing the first cluster bootstrap region.

Important APIs and types: `initial_region` creates the first `metapb::Region` with empty start/end keys, initial epoch constants, and one peer. `bootstrap_store` validates an empty KV default CF, writes `StoreIdent`, and syncs. `prepare_bootstrap_cluster` writes `PREPARE_BOOTSTRAP_KEY`, region local state, initial apply state, and initial raft state. `clear_prepare_bootstrap_cluster` removes prepared raft and KV metadata. `clear_prepare_bootstrap_key` removes only the prepare marker.

Control flow: Store bootstrap first checks range emptiness by scanning the KV engine. Cluster bootstrap writes KV metadata in one write batch, syncs KV, then writes initial raft state to the raft engine and consumes it synchronously. Clearing reverses this by cleaning raft logs/state and deleting prepare, region state, and apply state keys from KV.

State and persistence: This file writes durable store identity at `keys::STORE_IDENT_KEY`, the prepare marker at `keys::PREPARE_BOOTSTRAP_KEY`, region state and apply state in `CF_RAFT`, and initial raft state in the raft engine. Sync calls ensure bootstrap metadata reaches disk before success is returned.

Dependencies and integration points: It uses `engine_traits::Engines`, KV and raft engine traits, raftstore peer-storage initial state helpers, TiKV key layout helpers, and `tikv_util::store::new_peer`. It is used during store and cluster initialization before normal raftstore operation.

Risks: `bootstrap_store` checks only the default CF for emptiness before writing store identity, matching existing expectations but making CF assumptions important. Partial failure between KV prepare writes and raft initial state write can leave prepare metadata that must be cleared or retried. The generic comment notes raft engine lacks the same range-empty query, constraining type simplification.

Test signals: `test_bootstrap` verifies store bootstrap succeeds once and fails when repeated on non-empty KV, prepare writes all expected markers/states, clearing removes prepare metadata and raft data, and the raft log batch dump is empty after cleanup.
