# sources/storage-engines/tikv/components/raftstore-v2/src/operation/command/admin/conf_change.rs

Purpose: Implements raft configuration-change admin commands for raftstore-v2, covering proposal validation, legacy and v2 apply semantics, region-state mutation, raft-group membership update, PD/coprocessor notification, leader demotion/removal, and GC-peer metadata updates.

Important APIs/types/functions: `ConfChangeResult` captures applied index, raft `ConfChangeV2`, original `ChangePeerRequest`s, and resulting `RegionLocalState`. `UpdateGcPeersResult` carries updated region state. `Peer::propose_conf_change` rejects pending conf changes and serializes either v1 or v2 admin requests. `propose_conf_change_imp` uses `util::check_conf_change`, raft `propose_conf_change`, and metrics. `Peer::on_apply_res_conf_change` applies raft membership, updates storage region state, heartbeats PD, maintains peer heartbeat records, updates `StoreMeta`, read progress, and coprocessor events. `Apply::apply_conf_change`, `apply_conf_change_v2`, `apply_conf_change_imp`, `apply_leave_joint`, `apply_single_change_legacy`, `apply_single_change`, and `apply_update_gc_peer` perform apply-side region mutations.

Control flow: Proposal validates raft health and config rules, then raft proposes a sync-log conf change. Apply-side code determines simple/enter-joint/leave-joint kind, mutates peer roles and peer lists, advances conf version, records removed peers, tombstones self if removed, and returns an admin result. Peer-side result handling applies raft conf change when the log is still present, persists the new region state unless self is removed, and may step down if the leader is removed or demoted.

State and persistence behavior: Region metadata, peer roles, epoch conf version, removed/merged records, and tombstone state are persisted through region-state writes. In-memory raft membership, store meta, read progress, peer heartbeat maps, and coprocessor region-change notifications are synchronized with that persisted state.

Dependencies and integration points: It uses raft `ConfChangeV2`, raftstore utility validation, admin metrics, coprocessor region events, `StoreContext`, and underlying `Apply`/`Peer` region-state APIs.

Risks: Joint consensus transitions are complex; applying changes while still in joint state can panic. Duplicate same-store peers and mismatched removals are rejected. Proposal can be silently dropped by raft; this is mapped to `NotLeader`. Leader self-demotion/removal must step down promptly. Failpoints and TODOs indicate areas needing stronger coverage.

Test signals: Failpoint `apply_on_add_node_1_2` and comments around pending tests. Crate integration tests should cover v1/v2 changes, enter/leave joint, add learner/promote/demote/remove, self removal, redundant PD changes, and GC-peer record cleanup.
