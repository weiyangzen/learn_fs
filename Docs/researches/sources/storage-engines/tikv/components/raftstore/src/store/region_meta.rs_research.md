# sources/storage-engines/tikv/components/raftstore/src/store/region_meta.rs

## Purpose
`region_meta.rs` defines serde-friendly debug/status structures that expose raft and region metadata without requiring protobuf-generated types to derive serde directly. The output is a compact, serializable snapshot of peer state for diagnostics, inspection APIs, and tests.

## Important APIs, Types, and Functions
The file defines mirror enums and structs for raft progress and region metadata. `RaftProgressState` mirrors raft `ProgressState`. `RaftProgress` captures matched index, next index, state, pause flag, pending snapshot/request-snapshot indexes, and recent activity. `RaftHardState`, `RaftStateRole`, and `RaftSoftState` expose hard and soft raft state. `RaftStatus` aggregates raft node id, hard/soft state, applied index, voter and learner progress maps, last index, persisted index, and test-only unstable entry statistics.

Peer and region wrappers include `RaftPeerRole`, `Epoch`, `RegionPeer`, `RegionMergeState`, `RaftTruncatedState`, `RaftApplyState`, `RegionLocalState`, and top-level `RegionMeta`. Conversion implementations map raft/protobuf types into these serde structs, including bidirectional conversion between `RaftPeerRole` and `metapb::PeerRole`, plus equality helpers against protobuf peers.

The main constructor is `RegionMeta::new(local_state, apply_state, group_state, raft_status, last_index, persisted_index)`. It copies region id/range/epoch/peers, optional merge target state, tablet index, raft apply/truncate indexes, raft status, and group state into one serializable value.

## Control Flow
Construction starts from a protobuf `RegionLocalState`, protobuf `RaftApplyState`, a `GroupState`, raft `Status<'_>`, and caller-supplied log indexes. `RegionMeta::new` reads the embedded region, converts every peer into `RegionPeer`, converts merge state only if present, converts raft status through `From<raft::Status>`, then patches `last_index` and `persisted_index` because raft status itself does not supply those storage-level values. Bucket keys are initialized as an empty vector for later population by callers.

`From<raft::Status>` builds progress maps only when raft exposes progress, splitting entries into voters and learners according to the raft configuration. `From<ProgressState>` and `From<StateRole>` are exhaustive over current raft variants. Peer-role conversions are exhaustive over protobuf peer roles and preserve witness state separately at `RegionPeer`.

## State and Persistence Behavior
This module does not persist or mutate raftstore state. It snapshots in-memory/protobuf state into owned Rust structs containing primitive values, vectors, and maps. The serialized shape is intentionally independent from protobuf internals, which makes it useful for JSON/debug output but also means it must be maintained when raft or kvproto state grows.

## Dependencies and Integration Points
Dependencies are limited to `kvproto::{metapb, raft_serverpb}`, the raft crate's `Progress`, `Status`, and role enums, serde derives, and `super::GroupState`. The likely integration point is region/peer inspection code that wants a stable serializable `RegionMeta` rather than raw protobuf or raft structs. `replication_mode.rs` influences commit grouping but is separate from the `GroupState` carried here.

## Risks and Edge Cases
Because this is a mirror layer, drift is the main risk. New raft progress states, peer roles, local-state fields, bucket metadata fields, or unstable-entry fields can be silently omitted unless this file is updated. The voter/learner split depends on `progress.conf().voters().contains(*id)`; all non-voter progress is categorized as learner, which may hide more detailed joint-consensus roles in this debug projection. `RegionPeer::PartialEq<metapb::Peer>` converts into a protobuf peer and compares all populated fields, but comments acknowledge the comparison is conservative rather than a custom semantic match.

## Test Signals
There are no local tests in this file. Compile-time exhaustiveness checks cover enum conversions. Behavioral confidence depends on callers/tests that serialize or inspect `RegionMeta`, plus any testexport feature coverage for unstable entry metrics.
