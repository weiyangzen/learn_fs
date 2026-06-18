# sources/storage-engines/tikv/components/raftstore/src/store/fsm/life.rs

## Purpose

`sources/storage-engines/tikv/components/raftstore/src/store/fsm/life.rs` contains peer lifetime helper functions shared by the original raftstore FSM and raftstore v2 compatibility paths. Its scope is narrow but safety-critical: it constructs GC-peer response messages, forwards destroy checks from a merged target peer to a source peer, and lets compatible learners answer tombstone messages by inspecting persisted region state.

The file was read completely as a 98-line Rust module. It has no owned background tasks or structs; it is a helper module used by `store/fsm/store.rs` and `store/fsm/peer.rs`.

## Important APIs, Types, and Functions

`build_peer_destroyed_report(tombstone_msg: &mut RaftMessage) -> Option<RaftMessage>` builds an `ExtraMessageType::MsgGcPeerResponse` when a tombstone message proves that the addressed peer has been destroyed. If the incoming message already has an extra message, it asserts that the type is `MsgGcPeerRequest` and derives the destination region from `check_gc_peer.from_region_id`; otherwise it uses the message `region_id`. It refuses to build a response when the destination region id is zero or the original sender peer id is zero. The function consumes the incoming `to_peer` and `from_peer` via `take_to_peer` and `take_from_peer`, so callers should treat the input message as moved after calling it.

`forward_destroy_to_source_peer<T: FnOnce(RaftMessage)>(msg: &RaftMessage, forward: T)` converts a v2-style GC-peer request handled by a target peer into a tombstone raft message addressed to the merged source peer. It copies `check_region_id`, `check_peer`, `check_region_epoch`, and `from_region_id` from the request's `check_gc_peer` payload, sets `is_tombstone = true`, tags the extra message as `MsgGcPeerRequest`, and delegates transmission to the supplied closure.

`handle_tombstone_message_on_learner<EK: KvEngine>(engine: &EK, store_id: u64, mut msg: RaftMessage) -> Option<RaftMessage>` is the compatibility hook for learners such as TiFlash when `enable_v2_compatible_learner` is active. It reads `RegionLocalState` from the KV engine's raft column family under `keys::region_state_key(region_id)`. Missing or unreadable state is treated as a peer that may never have been created, and the function attempts to answer with `build_peer_destroyed_report`. If persisted state exists and is not `PeerState::Tombstone`, it returns `None`. If state is tombstone, it compares epochs and returns a destroyed report when the incoming epoch equals the local epoch or is stale relative to it.

## Control Flow

The store-level raft message handler in `store/fsm/store.rs` validates destination store id and region epoch first. When a message is tombstone and `enable_v2_compatible_learner` is true, it calls `handle_tombstone_message_on_learner`; any returned response is sent through the transport, and the original message is not routed to normal peer creation or peer FSM handling.

The peer-level extra message handler in `store/fsm/peer.rs` receives `MsgGcPeerRequest` only when v2 learner compatibility is enabled. `on_gc_peer_request` rejects malformed requests that lack `check_gc_peer` or have `extra_msg.index == 0`, waits until the local applied index reaches the request index, and then calls `forward_destroy_to_source_peer` to send a tombstone check to the source peer through `router.send_raft_message`.

`build_peer_destroyed_report` is the terminal response constructor for both direct tombstone handling and the missing-state path. Its output swaps sender and receiver peers, sets the response region, and attaches `MsgGcPeerResponse`.

## State and Persistence Behavior

The only persistent read in this module is `engine.get_msg_cf(CF_RAFT, &keys::region_state_key(region_id))`, decoded as `RegionLocalState`. No writes are performed. The persisted `PeerState::Tombstone` value and region epoch determine whether this local store can safely confirm destruction.

The module mutates in-memory `RaftMessage` values while building replies. That mutation is intentional but important: `take_to_peer` and `take_from_peer` empty those fields from the input. The forwarding helper builds a fresh tombstone message and does not mutate the original request.

## Dependencies and Integration Points

Direct dependencies include `engine_traits::{CF_RAFT, KvEngine}` for persisted region-local-state reads, `kvproto::raft_serverpb::{ExtraMessageType, PeerState, RaftMessage, RegionLocalState}` for raftstore wire messages and state, `keys::region_state_key` for the storage key, `crate::store::util::is_epoch_stale` for epoch safety checks, and `tikv_util::warn` for read failure diagnostics.

Primary integration points are the store FSM tombstone-message path, the peer FSM extra-message path, raftstore v2 GC-peer protocol compatibility, learner engines such as TiFlash, and merge cleanup flows where a target peer confirms source peer destruction. The behavior must remain consistent with raftstore v2's `Peer::on_gc_peer_request`, as noted by the caller.

## Risks and Edge Cases

The `assert_eq!` in `build_peer_destroyed_report` will panic if a caller passes a message with an unrelated extra message type. Current callers only pass tombstone or GC-peer request messages, but the helper is public within the module tree and relies on that contract.

The missing or unreadable `RegionLocalState` path sends a destroyed report. This is deliberate for skipped peer creation after snapshots, but a broad storage read failure can therefore be converted into a GC response. The warning includes store and region information, so operational logs are the main signal if this path is masking an engine problem.

Epoch handling is conservative: only equal or stale incoming epochs produce a response when tombstone state exists. Newer incoming epochs return `None`, avoiding acknowledgement against a local tombstone record that may not represent the requester's view.

Zero `from_region_id` or zero sender peer id suppresses the response. Corrupted GC-peer requests are also dropped earlier in `peer.rs` if required payload or index data is absent.

## Test Signals

Useful tests cover response construction for plain tombstone and `MsgGcPeerRequest` inputs, including sender/receiver peer swapping, `from_region_id` routing, and the `None` cases for zero ids.

Learner tombstone tests should exercise missing state, non-tombstone state, tombstone with equal epoch, tombstone with stale incoming epoch, and tombstone with newer incoming epoch. A mock `KvEngine` that returns read errors should verify that the warning path still attempts a destroyed report.

Integration tests should cover v1/v2 learner compatibility around merges: a peer receives `MsgGcPeerRequest`, waits for `applied_index >= extra_msg.index`, forwards a tombstone check to the source peer, and eventually emits `MsgGcPeerResponse`. Existing apply tests that enable `enable_v2_compatible_learner` are related signals, but this module benefits from direct unit coverage because the control flow is compact and protocol-sensitive.
