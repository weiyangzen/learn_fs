# sources/storage-engines/tikv/components/raftstore-v2/src/operation/command/admin/flashback.rs

Purpose: Implements prepare/finish flashback admin commands for raftstore-v2, toggling region flashback state and coordinating pessimistic lock behavior.

Important APIs/types/functions: `FlashbackResult` carries applied index and resulting `RegionLocalState`. `Peer::propose_flashback` serializes and proposes the admin request. `Apply::apply_flashback` handles `AdminCmdType::PrepareFlashback` and `FinishFlashback`, updates region `is_in_flashback` and `flashback_start_ts`, updates `PEER_ADMIN_CMD_COUNTER` and `PEER_IN_FLASHBACK_STATE`, and returns `AdminCmdResult::Flashback`. `Peer::on_apply_res_flashback` updates store metadata, read delegate/peer region state, persists region state, and updates pessimistic lock status.

Control flow: Proposal is a normal raft proposal. Apply toggles flashback fields in the in-memory apply region state and reports the result. Peer result handling optionally mutates state via failpoint, writes the region into `StoreMeta`, calls `set_region` with `RegionChangeReason::Flashback`, records a region-state write in `state_changes`, and adjusts pessimistic lock status based on flashback and leadership.

State and persistence behavior: Persistent state is the `RegionLocalState` written at the applied index. In-memory state includes store metadata, read delegate region, peer region, flashback metrics, and pessimistic lock table status. Entering flashback clears existing pessimistic locks and blocks new ones with `LocksStatus::IsInFlashback`.

Dependencies and integration points: It uses raftstore admin metrics, `LocksStatus`, coprocessor region-change reason, `StoreContext`, `ApplyResReporter`, and peer transaction context locks. It mirrors v1 behavior but notes v2 does not expire a remote lease because only local readers serve reads.

Risks: `meta.readers.get_mut(&region_id).unwrap()` assumes a reader exists for the region. Metrics must stay balanced across prepare/finish, especially repeated commands. The failpoint can simulate a peer FSM state mismatch. Lock status transitions depend on leadership after leaving flashback.

Test signals: Failpoint `keep_peer_fsm_flashback_state_false` exists. Integration should cover prepare/finish idempotence, metric gauge balance, lock clearing/blocking, follower lock status, and persistence of flashback start timestamp.
