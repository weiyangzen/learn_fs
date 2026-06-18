# sources/storage-engines/tikv/tests/failpoints/cases/test_disk_full.rs

Purpose: comprehensive disk usage behavior tests for raft proposals, transactions, follower reads, hibernation, merges, down peers, and majority-full decisions.

Important APIs and functions: helpers `assert_disk_full`, `disk_full_stores`, `get_fp`, `assert_region_leader_changed!`, and `ensure_disk_usage_is_reported!`. Tests cover leader/follower behavior, txn operations with `DiskFullOpt`, majority full, hibernated followers, merge under majority full, mixed almost/already full stores, down nodes, and follower read-index rejection.

Control flow: failpoints `disk_almost_full_peer_N` and `disk_already_full_peer_N` simulate store status; tests force reports through read-index, issue raft commands or KV RPCs, and assert accepted/rejected paths and leader movement.

State and persistence: raft local state indexes verify whether entries were appended; engines verify value replication or absence. PD down-peer and disk status reports affect scheduling decisions.

Dependencies and integration: uses node/server clusters with v2 variants, `kvproto::disk_usage`, raft command options, transaction client helpers, and raft packet filters.

Risks and test signals: many scenarios depend on disk usage report propagation and sleeps. Signals are exact store IDs in errors, safe admission of special operations, and blocked unsafe writes.
