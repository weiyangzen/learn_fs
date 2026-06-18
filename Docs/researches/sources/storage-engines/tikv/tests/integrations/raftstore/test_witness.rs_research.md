# sources/storage-engines/tikv/tests/integrations/raftstore/test_witness.rs

Purpose: exercises raftstore witness peer invariants. Witness peers should replicate raft metadata/logs without holding user data, serving reads, or becoming leaders.

Important APIs and functions: `PdClient::must_switch_witnesses`, `new_witness_peer`, `find_peer`, `must_get_error_is_witness`, `RegionPacketFilter`, `IsolationFilterFactory`, `RaftApplyState`, and `PeerState`. Tests cover split/merge, conf changes, witness switching, leader/election restrictions, log GC, replica reads, leader-down behavior, consistency checks, and snapshot recovery.

Control flow: tests usually start a three-node server cluster, disable default PD operators, switch a peer to witness, and assert user data is absent while raft metadata advances. Split/merge tests verify witness flags propagate and reject merges with different witness placement. Log-GC tests compare truncated states while a follower or witness lags. Snapshot isolation tests force snapshot application to a witness after network isolation.

State and persistence: witness peers update apply state, region local state, region epoch, truncated state, and tombstones but must not store KV values. Tests inspect engine contents and raftstore metadata directly.

Dependencies and integration: PD operators, raft conf changes, raftstore cluster helpers, packet filters, raft apply metadata, and TiKV witness-peer utility constructors.

Risks: sleeps around conversion, replication, consistency checks, and snapshot transfer can be timing-sensitive. Some assertions depend on precise error messages and current raftstore scheduling behavior.

Test signals: passing tests show witnesses remain metadata-only, cannot lead or serve reads, preserve topology through split/merge, do not incorrectly block log GC, and recover after snapshot isolation.
