# sources/storage-engines/tikv/components/raftstore-v2/src/raft/peer.rs

Purpose: this file defines `Peer`, the central raftstore-v2 object that wraps a raft `RawNode<Storage>`, current tablet cache, proposal/read queues, lifecycle state, split/merge/compact contexts, unsafe recovery state, transaction context, and readiness flags.

Important APIs/types/functions: `Peer::new` builds a peer from config, tablet registry, snap manager, and `Storage`. The remainder provides accessors and orchestration helpers for region/peer metadata, tablet replacement, read progress, leader lease, raft group, apply scheduler, proposal queue, pending ticks/messages, state changes, split/merge contexts, force-leader state, unsafe recovery state, and transfer-leader state.

Control flow: construction creates a raft config using applied index, recovers and loads a tablet if initialized, creates a cached tablet handle, initializes read progress and lease, restores merge proposal-control state if needed, and campaigns immediately for a single-peer initialized region. `set_region` updates region metadata, tablet index, read delegate/progress, leader lease, transaction context, and coprocessor region-change notifications. Ready helpers (`set_has_ready`, `set_has_extra_write`, pending messages/ticks) drive batch FSM processing.

State and persistence: peer-owned persistent deltas are accumulated in `state_changes` log batches and merged into `WriteTask` via `merge_state_changes_to`. `flush_state`, `sst_apply_state`, compact-log context, last sent snapshot index, and persistent tablet index interactions coordinate log GC and tablet durability. The peer stores only cached/live state for leadership, reads, proposals, and recovery, while `Storage` owns raft local/apply/region state.

Dependencies/integration: depends on raft `RawNode`, engine tablet cache/registry, coprocessor host, raftstore proposal/read queues, leases, region read progress, unsafe recovery states, transaction context, and many operation contexts. It is extended by numerous `operation/*` impl blocks.

Risks: `Peer` is a high-coupling object; subtle flag omissions can prevent ready handling, async writes, or ticks. Region updates must keep storage, read delegate, read progress, lease, and transaction context consistent. Force-leader and unsafe recovery states live here and bypass normal raft assumptions.

Test signals: no direct unit tests in this file. Behavior is covered through operation and raftstore-v2 integration tests that instantiate peers and exercise lifecycle transitions.
