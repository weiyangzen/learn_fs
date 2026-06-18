<!-- BEGIN_FILE_RESEARCH: sources/storage-engines/tikv/tests/integrations/raftstore/test_life.rs -->
# sources/storage-engines/tikv/tests/integrations/raftstore/test_life.rs

## Purpose
This integration test file exercises raftstore peer lifecycle cleanup paths, especially garbage collection of removed peers, learner peers, and v2-compatible TiFlash-like learner behavior. It focuses on the correctness of tombstone/removed-record handling when peers are removed before creation, after learner creation, while isolated, or while their role changes through conf change.

## Important APIs, Types, and Functions
`ForwardFactory` and `ForwardFilter` implement `FilterFactory`/`Filter` to intercept `RaftMessage`s and optionally forward them into another cluster router. This is used to cross-wire v1 and v2 raftstore simulations in `test_gc_peer_tiflash_engine`.

The test functions are `test_gc_peer_tiflash_engine`, `test_gc_removed_peer`, and `test_gc_peer_with_conf_change`. They use `new_node_cluster`, `run_conf_change`, `new_peer`, `new_learner_peer`, `new_change_peer_request`, `new_admin_request`, `RegionPacketFilter`, `ExtraMessageType::MsgGcPeerRequest`, and `MsgGcPeerResponse`.

## Control Flow and Behavior
`test_gc_peer_tiflash_engine` boots v1 and v2 node clusters with matching learner state, forwards leader/learner traffic between the clusters, removes a learner from the v2 cluster, and waits for the v2 leader to clear removed records. `test_gc_removed_peer` synthesizes GC peer requests and verifies responses for a learner that never fully existed and for a learner that was added, tombstoned, and later collected. `test_gc_peer_with_conf_change` isolates an added learner, promotes/removes it through explicit admin conf-change requests, then sends a tombstone raft message addressed as a voter while the isolated local peer still sees itself as a learner.

## State and Persistence
The tests inspect raft local state, region local state, apply state, peer roles, `PeerState::Normal`/`Tombstone`, removed-record emptiness, and region epoch increments. They validate that lifecycle metadata persists enough to answer GC requests but is eventually cleaned after tombstone handling.

## Dependencies and Integration Points
The file depends on `kvproto` raft server metadata, raft message types, raftstore test transport filters, v1/v2 cluster simulators, PD conf-change helpers, and TiKV timing utilities. It integrates directly with raftstore message routing and peer cleanup paths rather than only using public KV operations.

## Risks
The tests are timing-sensitive because cleanup is tick-driven and message forwarding crosses simulated clusters. They also rely on exact peer IDs and region IDs. Regressions may appear as leaked removed records, peers stuck in learner/voter mismatch, or GC responses not emitted for tombstoned peers.

## Test Signals
Strong signals are successful `must_empty_region_removed_records`, expected `PeerState` transitions, equality of v1/v2 local raft/apply state before forwarding, and no errors from conf-change admin requests. Timeouts indicate lifecycle cleanup or forwarding regressions.
<!-- END_FILE_RESEARCH: sources/storage-engines/tikv/tests/integrations/raftstore/test_life.rs -->
