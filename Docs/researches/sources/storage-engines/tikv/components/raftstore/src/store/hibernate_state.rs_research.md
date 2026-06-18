# `sources/storage-engines/tikv/components/raftstore/src/store/hibernate_state.rs`

## Purpose
This file models raft group hibernation state. It lets a leader negotiate whether a region can move from active replication into an idle hibernated state, while preserving compatibility with older TiKV versions through PD feature gating.

## Important APIs, Types, and Functions
- `NEGOTIATION_HIBERNATE` requires feature version 5.0.0 before broadcasting the negotiation protocol.
- `GroupState` is the serialized group-level state: `Ordered`, `Chaos`, `PreChaos`, or `Idle`.
- `LeaderState` tracks local leader negotiation state: `Awaken`, `Poll(Vec<u64>)`, or `Hibernated`.
- `HibernateState` combines group and leader state.
- `HibernateState::ordered` creates an active ordered state.
- `reset` changes group state, updates `HIBERNATED_PEER_STATE_GAUGE`, and wakes leader state unless the new group state is `Idle`.
- `count_vote` records one peer's hibernate vote during polling, deduplicated by peer id.
- `should_bcast` checks whether the feature gate allows hibernate negotiation.
- `maybe_hibernate` performs the leader-side vote/quorum/down-peer decision and returns `(hibernated, vote_peer_ids)`.

## Control Flow
The leader starts in `LeaderState::Awaken`. The first `maybe_hibernate` call moves it to `Poll` and returns false so peers can be asked to vote. Later calls include votes via `count_vote`. `maybe_hibernate` builds a vote set including the leader, checks for alive peers that have not voted and are not listed as down, allows quorum-based progress when non-voters are down, and finally enters `LeaderState::Hibernated` only if every peer is either leader, voted, or down.

## State and Persistence Behavior
`GroupState` derives `Serialize` and `Deserialize`, so it can cross message/config/storage boundaries where higher-level raftstore code chooses to persist or transmit it. This file itself performs no disk IO. State changes are in memory and reflected through `HIBERNATED_PEER_STATE_GAUGE`; `Idle` and `PreChaos` count as hibernated for the gauge, while `Ordered` and `Chaos` count as awaken.

## Dependencies and Integration Points
The code depends on `kvproto::metapb::Region` for peer lists, `pd_client::FeatureGate` for compatibility, `collections::HashSet` for vote/quorum sets, and raftstore metrics. It is re-exported by `store/mod.rs` as `GroupState` and `HibernateState`, then used by peer logic to negotiate quiet raft groups.

## Risks and Edge Cases
- The feature gate is important because older binaries cannot recognize the negotiation protocol and may reset connections.
- Down-peer handling allows hibernation with quorum even without every peer vote; correctness depends on the caller's `down_peer_ids` and quorum predicate being accurate.
- `reset` ignores same-state transitions, so gauge initialization depends on callers accounting for initial states elsewhere.
- `vote_peer_ids` is built from a hash set, so its order is intentionally unstable and should not be used as an ordered protocol.

## Test Signals
There are no local tests. Valuable coverage would include first-call polling transition, duplicate votes, all-voted hibernation, quorum-with-down-peers hibernation, alive-non-voter rejection, `reset` metric transitions, and feature-gate behavior.
