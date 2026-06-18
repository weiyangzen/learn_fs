# sources/storage-engines/tikv/components/raftstore/src/store/util.rs

## Purpose
This file is the raftstore store utility hub. It concentrates correctness-sensitive helpers for region key membership, raft first-message classification, empty snapshot construction, epoch validation, flashback request admission, leader lease tracking, raft entry decoding, region sibling/conf-state conversion, configuration-change safety validation, stale-read safe-ts tracking, and split validation. Most logic here is shared by peers, local reads, store message handling, split/merge flows, and admin command proposal/application.

## Important APIs, Types, and Functions
- Key and epoch helpers: `check_key_in_region_exclusive`, `check_key_in_region_inclusive`, `check_key_in_region`, `is_epoch_stale`, `check_req_region_epoch`, `check_region_epoch`, `compare_region_epoch`, `is_region_epoch_equal`, and `validate_split_region`.
- Raft message helpers: `is_first_append_entry`, private `is_first_vote_msg`, `is_first_message`, `is_vote_msg`, and `is_initial_msg` decide whether unknown-region raft traffic can initialize or should wait behind pending splits.
- Snapshot and command decoding helpers: `new_empty_snapshot`, `get_entry_header`, `parse_data_at`, `RaftCmd`, and `parse_raft_cmd_request`.
- Lease types: `Lease`, `RemoteLease`, and `LeaseState` encode leader lease validity/suspicion and expose a thread-shareable remote view for local-read threads.
- Configuration change abstractions: `AdminCmdEpochState`, `admin_cmd_epoch_lookup`, `ConfChangeKind`, `ChangePeerI`, and `check_conf_change` bridge legacy and v2 change-peer requests to raft-rs `ConfChangeI`.
- Read progress types: `RegionReadProgressRegistry`, `RegionReadProgress`, `RegionReadProgressCore`, `ReadState`, and `LocalLeaderInfo` track stale-read `safe_ts`/resolved-ts by region and publish leader identity plus applied-index-gated read states.
- Miscellaneous helpers: `gen_bucket_version`, `conf_change_type_str`, `build_key_range`, `is_region_initialized`, `u64_to_timespec`, `is_sibling_regions`, `conf_state_from_region`, `KeysInfoFormatter`, and `MsgType`.

## Control Flow
Request admission typically validates target store/peer/term, checks the request epoch according to normal-vs-admin command policy, and optionally checks flashback state. Epoch comparison is strict for the selected dimensions, returning `EpochNotMatch` with optional current region metadata.

First raft-message classification is used when a store receives raft messages for an unknown or overlapping region. Initial vote/pre-vote terms, first append entries, and heartbeat messages with `INVALID_INDEX` commit carry different creation/pending semantics.

Lease control starts with `Lease::renew`, `suspect`, `expire`, or `maybe_new_remote_lease`. The local lease owns the authoritative bound; `RemoteLease` receives atomic expiry updates only when bounds advance far enough, and `need_renew` asks for proactive renewal near the configured advance window.

Configuration changes are first simulated through raft-rs `Changer`, then checked for raftstore-level safety: operation/role matching, duplicate peer IDs, witness-switch rejection, leader removal/demotion policy, learner-only joint-change rejection, heartbeat-based availability, and log-availability safety via `maximal_committed_index`.

Read progress flows through `RegionReadProgress::update_safe_ts_with_time` and `update_applied`. Safe-ts records with future apply indexes are queued in sorted `pending_items`; once applied index catches up, the highest eligible ts is published through atomics and coprocessor hooks. Merges call `merge_safe_ts`, consume items through the merge index, lower target safe-ts to the source/target minimum, and reject stale pre-merge items thereafter.

## State and Persistence Behavior
Most state is in-memory but mirrors persistent raft/apply facts. `Lease` stores monotonic-clock bounds and has no durable persistence; lease loss is encoded by clearing the bound and expiring the remote atomic view. `timespec_to_u64` compresses monotonic times to millisecond precision for atomic sharing.

`RegionReadProgressCore` persists no data itself, but its `applied_index`, `read_state`, `pending_items`, `last_merge_index`, pause/discard flags, leader info, and diagnostic timestamps derive from applied raft progress, resolved-ts publication, leader check RPCs, and region metadata. The public `safe_ts` and `read_index_safe_ts` atomics are fast paths for read execution.

`new_empty_snapshot` serializes `RaftSnapshotData` containing region metadata, zero file size, current snapshot version, and witness flag into the raft snapshot data field. Entry parsing supports both simple-write v2 decoding and legacy protobuf raft command payloads.

## Dependencies and Integration Points
This file depends on `kvproto` region, raft command, raft server, and kvrpc types; raft-rs `RawNode`, `Changer`, `ConfState`, entries, and messages; `engine_traits::KvEngine`; `tikv_util` logging/time/codec helpers; `txn_types::WriteBatchFlags`; `tokio::sync::Notify`; and crate modules for config, metrics, peer storage, snapshots, simple-write decoding, and coprocessor hooks.

Integration is broad: peer proposal/application uses epoch, term, peer, flashback, and split validation; local read workers use `Lease` and `RemoteLease`; stale-read and check-leader workers use `RegionReadProgressRegistry`; raftstore membership paths use `ChangePeerI` and `check_conf_change`; snapshot generation and application use conf-state and empty snapshot helpers.

## Risks and Edge Cases
Epoch policy is explicitly compatibility-sensitive; comments warn against changing `admin_cmd_epoch_lookup` or normal-request epoch flags. `parse_data_at` and legacy header extraction panic on corrupted raft entry data, relying on upstream raft-entry integrity. `RegionReadProgressRegistry::with` holds a mutex during callback execution and warns against nested locking. Safe-ts lowering on merge is subtle; missing `last_merge_index` filtering could incorrectly raise safe-ts after merge. Witness peers pause/discard stale-read progress to prevent serving stale reads. Configuration-change checks mix raft simulation, heartbeat freshness, and store policy, so role mapping or heartbeat threshold changes can affect availability.

## Test Signals
The module has focused tests for lease state transitions and remote lease expiry, timespec encoding, raft command header extraction, conf-state generation, change-peer v2 transition selection, first vote/append/initial message classification, epoch staleness and request epoch policy, sibling detection, store/peer/term mismatch errors, read-progress pending queue behavior, leader-info updates, heartbeat-based conf-change availability rejection, unhealthy-cluster exceptions, and `read_index_safe_ts` pause/discard/merge reset behavior.
