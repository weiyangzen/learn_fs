# sources/storage-engines/tikv/components/raftstore-v2/src/operation/life.rs

## Purpose
Implements raftstore-v2 peer creation, peer destruction, tombstone handling, stale peer garbage collection, merge-source destruction coordination, availability probes, and disk-full proposal gating. The module explains the v2 lifecycle model: peers are created only by bootstrap, store-level raft messages, or split-init via a store-created uninitialized FSM; peers are destroyed only after removal/merge/tombstone/larger-peer-id paths persist a tombstone record.

## Important APIs, Types, And Functions
`DestroyProgress` tracks destroy state from `None` to `WaitReady`, `Destroying`, and `Destroyed`, optionally carrying the triggering raft message used to recreate a newer peer after destruction. `AbnormalPeerContext` stores pending peers, down peers, disk-full peers, and whether a dangerous majority set exists. `GcPeerContext` stores peer ids confirmed as destroyed. Store-level entry points include `Store::on_split_init`, `Store::on_ask_commit_merge`, and `Store::on_raft_message`. Peer-level entry points include `maybe_schedule_gc_peer_tick`, `maybe_gc_sender`, `on_tombstone_message`, `on_gc_peer_request`, `on_gc_peer_response`, `on_gc_peer_tick`, `check_proposal_with_disk_full_opt`, `refill_disk_full_peers`, `mark_for_destroy`, `postponed_destroy`, `start_destroy`, and `finish_destroy`.

## Control Flow
Store-level raft messages are first attempted against an existing peer mailbox. If the mailbox is disconnected, the store validates store id, epoch, tombstone state, merge target state, and disk-full constraints before creating an uninitialized `Storage` and `PeerFsm`, registering it with the router, and forwarding the original message when it has a valid sender. Split initialization creates the recipient peer through an empty split message, then sends `PeerMsg::SplitInit`. Tombstone and larger-peer-id messages mark an existing peer for asynchronous destruction. GC ticks are leader-only: removed peers receive direct tombstone messages, while merged source peers are checked through target peers before source destruction is forwarded.

## State And Persistence Behavior
Destroy is deliberately asynchronous. `mark_for_destroy` only moves the peer into `WaitReady` and forces a ready round. `start_destroy` waits until pending apply and tombstone-tablet work are safe, cleans raft-engine state through the extra write batch, writes `PeerState::Tombstone` at the applied index, records tombstone tablet cleanup, and moves to `Destroying`. `finish_destroy` runs only after the destroy write is persisted; it removes store metadata, reader delegates, read progress, tablet registry entries, closes the router mailbox, clears pending reads and proposals, and dispatches any saved triggering message. Removed and merged peer records remain in region state until an `UpdateGcPeer` admin proposal removes confirmed ids.

## Dependencies And Integration Points
The module depends on raft engine region state reads, `Storage::uninit`, `PeerFsm::new`, router registration, raftstore transport, split and merge command helpers, tablet registry cleanup, disk usage state from the store context, proposal control, apply proposal callbacks, and PD heartbeat side effects. It integrates tightly with `ready/mod.rs` because ready handling is where destroy writes are built and finalized.

## Risks And Edge Cases
The main risks are lifecycle races: split-init racing with initial raft messages, recreating a peer after a larger id tombstones the old peer, forwarding merge-source GC only after target merge completion, and preventing tablet path races during destroy. Disk-full logic is also safety-sensitive because it can suppress proposals, transfer leadership, reduce raft inflight messages to disk-full peers, and keep a potential quorum alive. `check_if_to_peer_destroyed` can panic if the raft engine reports a non-tombstone state for a peer that does not exist in memory.

## Test Signals
No local test module appears in this file. Observable signals are failpoint coverage around split-init races, raft metrics for dropped messages, tombstone and GC logs, disk-full proposal errors, `UpdateGcPeer` admin proposals, and integration tests that exercise split, merge, peer removal, unsafe recovery destroy, and disk-full behavior.
