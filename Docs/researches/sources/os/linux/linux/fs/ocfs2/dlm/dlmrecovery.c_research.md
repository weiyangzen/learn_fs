# File Research: sources/os/linux/linux/fs/ocfs2/dlm/dlmrecovery.c

## Purpose
Implements OCFS2 DLM cluster recovery after node death, including recovery master election, lock resource remastering, migrated lock state transfer, local cleanup, heartbeat callbacks, and recovery finalization.

## Major Responsibilities
- Runs the recovery kernel thread via `dlm_launch_recovery_thread()`, `dlm_recovery_thread()`, and `dlm_complete_recovery_thread()`.
- Tracks recovery state in `dlm->reco`: `dead_node`, `new_master`, `state`, `node_data`, `resources`, and recovery maps.
- Elects a recovery master using the special `$RECOVERY` lock in `dlm_pick_recovery_master()`.
- Performs recovery-master duties in `dlm_remaster_locks()`: allocate node recovery area, request lock state from surviving nodes, wait for all recovery data, finalize ownership, and wake normal DLM processing.
- Sends and handles network messages:
  - `DLM_BEGIN_RECO_MSG`
  - `DLM_LOCK_REQUEST_MSG`
  - `DLM_MIG_LOCKRES_MSG`
  - `DLM_RECO_DATA_DONE_MSG`
  - `DLM_MASTER_REQUERY_MSG`
  - `DLM_FINALIZE_RECO_MSG`
- Migrates one lock resource’s full queue state with `dlm_send_one_lockres()`, `dlm_send_mig_lockres_msg()`, `dlm_mig_lockres_handler()`, and `dlm_process_recovery_data()`.
- Cleans local state on node death in `dlm_do_local_recovery_cleanup()` by marking dead-owned resources recovering, pruning dead-node locks, clearing refmap bits, and invalidating LVBs when needed.
- Hooks cluster heartbeat events through `dlm_hb_node_down_cb()` and `dlm_hb_node_up_cb()`.

## Key Recovery Flow
1. Heartbeat reports a node down.
2. `__dlm_hb_node_down()` clears live/domain state, runs local cleanup, notifies DLM users, sets the node in `recovery_map`, and wakes recovery.
3. Recovery thread picks the first node in `recovery_map`.
4. If no recovery master exists, nodes race for `$RECOVERY` EX lock.
5. Winner sends begin-recovery messages and becomes `reco.new_master`.
6. Recovery master requests all locks from each surviving node.
7. Non-master nodes move relevant recovering resources to a temporary list and send lock state packets.
8. Recovery master processes incoming locks, reconstructs queues, handles dummy mastery refs, and waits for `DATA_DONE`.
9. Master sends two-stage finalize messages.
10. All nodes call `dlm_finish_local_lockres_recovery()`, clear recovery flags, reset recovery state, and resume normal DLM work.

## Important Data Handling
- `dlm_mig_cookie` identifies multi-packet lockres transfers when a resource has more than `DLM_MAX_MIGRATABLE_LOCKS`.
- `dlm_migratable_lockres` carries lock name, owner, flags, total lock count, LVB, cookie, and an array of migratable locks.
- Dummy locks represent a refmap/mastery reference when a lockres has no actual locks.
- LVB migration is carefully validated:
  - blocked locks do not carry valid LVB data;
  - EX/PR locks are candidates;
  - mismatched non-empty LVBs cause diagnostic logging and `BUG()`.

## Concurrency and Synchronization
- `dlm->spinlock` protects domain/recovery maps and lockres hash/list membership.
- Per-resource `res->spinlock` protects lock queues, ownership, state flags, refmaps, and LVB handling.
- `dlm_reco_state_lock` protects `dlm->reco.node_data`.
- `dlm_mig_cookie_lock` serializes migration cookie allocation.
- Work is deferred through `dlm->work_list`, `dlm->work_lock`, `dlm->dlm_worker`, and `dlm_dispatch_work()` so network handlers can queue sleepable processing.
- Recovery blocks normal top-level lock/unlock work through `DLM_RECO_STATE_ACTIVE`; waiters use `dlm_wait_for_recovery()`.

## Failure and Edge Cases
- Recovery master death is detected by seeing `new_master` in `recovery_map`; master is cleared and election can restart.
- Finalize stage uses `DLM_RECO_STATE_FINALIZE` and a two-phase message to avoid starting a new recovery before all nodes have completed the previous one.
- If a node dies while sending recovery data, the sender skips `ALL_DONE`; the recovery master notices node death while waiting.
- Master requery handles rare migration/node-death races where a lockres owner is unknown.
- Allocation failure during recovery is treated as retryable in several places, but some inconsistencies intentionally call `BUG()` because DLM state corruption would be fatal.
- Special `$RECOVERY` lock entries for dead nodes are pruned to avoid later hangs.

## External Dependencies
Depends on OCFS2 cluster heartbeat, node manager, o2net messaging, DLM common/domain APIs, lock resource hashing/refcounting helpers, AST/BAST infrastructure, and DLM lock/unlock APIs.
