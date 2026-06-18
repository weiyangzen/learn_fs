# File Research: sources/os/linux/linux-stable/fs/ocfs2/dlm/dlmrecovery.c

## Purpose

Implements OCFS2 DLM recovery after cluster node death, including recovery-master election, local cleanup of stale lock state, remastering lock resources formerly owned by the dead node, lock-resource migration/reconstruction, and two-stage recovery finalization.

This is a central correctness file for cluster lock manager failover. It coordinates heartbeat events, DLM lock queues, network recovery messages, worker queues, and lock resource ownership transitions.

## Major Responsibilities

- Maintain recovery state in `dlm->reco`, including:
  - `dead_node`
  - `new_master`
  - active/finalize state flags
  - `recovery_map`
  - recovery resource list
  - per-node recovery data list
- Run the recovery kernel thread.
- Elect a recovery master using the special `$RECOVERY` lock.
- Notify other nodes of recovery begin/finalize phases.
- Request and receive all lock state from surviving nodes.
- Serialize migratable lock resource state into network messages.
- Reconstruct received lock resources and lock queues.
- Clean local stale state when heartbeat reports a node down.
- Handle recovery master death and repeated recovery attempts.

## Important Entry Points

- `dlm_launch_recovery_thread()` starts the per-domain recovery kthread.
- `dlm_complete_recovery_thread()` stops it.
- `dlm_kick_recovery_thread()` wakes it.
- `dlm_hb_node_down_cb()` and `dlm_hb_node_up_cb()` receive heartbeat events.
- `dlm_request_all_locks_handler()` handles recovery-master requests for local lock state.
- `dlm_reco_data_done_handler()` records completion from a node.
- `dlm_mig_lockres_handler()` handles migrated or recovered lock-resource packets.
- `dlm_master_requery_handler()` answers owner requery messages.
- `dlm_begin_reco_handler()` handles remote recovery start notification.
- `dlm_finalize_reco_handler()` handles recovery finalize phases.
- `dlm_send_one_lockres()` serializes a lock resource for recovery or migration.
- `dlm_move_lockres_to_recovery_list()` marks a lock resource recovering and places it on the recovery list.

## Recovery Thread Flow

`dlm_recovery_thread()` periodically calls `dlm_do_recovery()` once the domain is fully joined.

`dlm_do_recovery()`:

1. Skips work if all lock resources have migrated away.
2. Detects recovery-master death.
3. Chooses the next dead node from `recovery_map`.
4. Marks recovery active with `dlm_begin_recovery()`.
5. Elects a recovery master if one is not already known.
6. If another node is master, ends the local recovery barrier after local resources have been marked.
7. If this node is master, calls `dlm_remaster_locks()`.
8. On success, resets recovery state and immediately loops to find more dead nodes.

The active recovery flag intentionally blocks normal top-level DLM API paths until affected lock resources have been marked with recovery state.

## Recovery Master Election

`dlm_pick_recovery_master()` repeatedly attempts to acquire the special `$RECOVERY` lock in exclusive mode with `LKM_NOQUEUE | LKM_RECOVERY`.

Outcomes:

- `DLM_NORMAL`: this node acquired the recovery lock and may become master.
- `DLM_NOTQUEUED`: another node likely won; wait for `reco.new_master`.
- `DLM_RECOVERING`: retry because the previous master died.
- Anything else is treated as a severe consistency error and can BUG.

If this node wins, it sends `DLM_BEGIN_RECO_MSG` to peers through `dlm_send_begin_reco_message()`, then records itself as `reco.new_master`.

## Remastering Protocol

`dlm_remaster_locks()` is the master-side recovery protocol.

It:

1. Builds `dlm->reco.node_data` from current domain membership via `dlm_init_recovery_area()`.
2. Requests all relevant lock state from each live node via `dlm_request_all_locks()`.
3. Tracks each node through recovery states:
   - `INIT`
   - `REQUESTING`
   - `REQUESTED`
   - `RECEIVING`
   - `DONE`
   - `DEAD`
   - `FINALIZE_SENT`
4. Waits until all nodes are done or dead.
5. Sets `DLM_RECO_STATE_FINALIZE`.
6. Sends two-stage finalize messages with `dlm_send_finalize_reco_message()`.
7. Locally finishes lockres recovery with `dlm_finish_local_lockres_recovery()`.
8. Kicks the regular DLM thread to rescan dirty lock resources.

Node failures during this process are tolerated when recognized as host-down conditions. Allocation or transient network errors generally trigger retries.

## Lock State Export

When a node receives `DLM_LOCK_REQUEST_MSG`, `dlm_request_all_locks_handler()` queues `dlm_request_all_locks_worker()` on the DLM worker.

The worker:

- Validates the requested `dead_node` and recovery master.
- Moves lock resources owned by the dead node or with unknown owner from `dlm->reco.resources` to a temporary list.
- Sends each lock resource to the recovery master with `dlm_send_one_lockres()`.
- Sends `DLM_RECO_DATA_DONE_MSG` unless the recovery master died.
- Moves resources back to `dlm->reco.resources`.

Special `$RECOVERY` lock resources are pruned so stale recovery-lock grants from dead nodes do not stall later recovery.

## Migratable Lock Resource Format

`dlm_init_migratable_lockres()` initializes a page-sized `struct dlm_migratable_lockres`.

`dlm_send_one_lockres()` serializes all locks from:

- granted queue
- converting queue
- blocked queue

It may split large lock resources across multiple messages using a migration cookie. Empty lock resources are represented by a dummy lock so mastery/refmap information is still conveyed.

`dlm_prepare_lvb_for_migration()` selects a valid lock value block from eligible EX/PR locks and checks that all valid LVB copies agree. Mismatches are treated as fatal consistency errors.

## Lock State Import

`dlm_mig_lockres_handler()` handles received migrated/recovered lock resources.

It:

- Validates domain state and message type.
- Finds or creates the local lock resource.
- Marks it as recovering or migrating.
- Inserts newly created lock resources into the hash.
- Takes refs needed for asynchronous worker processing.
- Queues `dlm_mig_lockres_worker()`.

`dlm_mig_lockres_worker()` may requery ownership if the message had unknown owner, then calls `dlm_process_recovery_data()`.

`dlm_process_recovery_data()` reconstructs locks:

- Dummy lock: sets refmap only.
- Local-node lock during migration: reorders existing local lock without replacing it.
- Remote-node lock: allocates a new `dlm_lock`, attaches it to the lockres, restores type/convert state/flags, restores LVB when valid, and adds it to the correct queue.

The function has strict BUG checks for duplicate cookies, impossible queue state, mismatched local lock nodes, invalid LVB state, and inconsistent migration semantics.

## Master Requery

`dlm_lockres_master_requery()` and `dlm_do_master_requery()` handle the rare case where migration intersects with node death and ownership is unknown.

The requery asks surviving nodes whether a lock resource has a real master. If all answers are unknown, the local node may take ownership. If another valid master exists, the imported lockres is not touched further.

`dlm_master_requery_handler()` answers with local owner information and dispatches assert-master work when this node owns the resource.

## Local Cleanup On Node Death

Heartbeat down events enter through `dlm_hb_node_down_cb()` and `__dlm_hb_node_down()`.

`__dlm_hb_node_down()`:

- Handles recovery master death.
- Clears join state if the joining node died.
- Ignores already-dead or irrelevant nodes.
- Clears the node from live/domain/exit maps.
- Performs local cleanup before notifying heartbeat listeners.
- Wakes migration waiters.
- Sets the node in `recovery_map`.

`dlm_do_local_recovery_cleanup()` scans all lock resources:

- Cleans stale master-list entries.
- Prunes `$RECOVERY` locks for the dead node.
- Revalidates/invalidates LVBs as needed.
- Moves lock resources owned by the dead node to the recovery list.
- Frees locks belonging to the dead node when this node is master.
- Clears dead-node refmap bits for unknown-owner resources where appropriate.

`dlm_move_lockres_to_recovery_list()` also resolves pending lock/convert/unlock/cancel state before recovery export.

## Finalization

Finalization is two-stage.

`dlm_send_finalize_reco_message()` sends `DLM_FINALIZE_RECO_MSG` to every live domain node twice:

1. Stage 1: peers call `dlm_finish_local_lockres_recovery()`, set finalize state.
2. Stage 2: peers verify stage 1 happened, clear finalize state, reset recovery state, and kick their recovery thread.

This protects against starting a new recovery before the previous one is fully finalized cluster-wide.

## Concurrency And Synchronization

Key synchronization mechanisms:

- `dlm->spinlock` protects domain/recovery maps and many lockres-list transitions.
- `res->spinlock` protects per-lock-resource queues and state.
- `dlm_reco_state_lock` protects `reco.node_data`.
- `dlm_mig_cookie_lock` protects the migration cookie counter.
- `dlm->dlm_reco_thread_wq` wakes recovery waiters/thread.
- `dlm->reco.event` releases API callers blocked on active recovery.
- Work items use `dlm->work_lock`, `dlm->work_list`, and `dlm->dlm_worker`.

The code frequently drops locks before network sends or sleeping, then revalidates state afterward.

## Notable Edge Cases

- Recovery master death during recovery or finalize.
- Begin-recovery compatibility with peers returning `EAGAIN` instead of `-EAGAIN`.
- Lock resources with unknown owners.
- Node death during lock-resource migration.
- Unlock/cancel/convert pending when master dies.
- Dead node holding `$RECOVERY`.
- Empty lock resources needing dummy migration records.
- LVB invalidation when EX/PR state cannot prove validity.
- Host-down errors are often nonfatal; unexpected network errors often BUG.

## Dependencies

- OCFS2 cluster heartbeat, node manager, and TCP messaging.
- DLM common/domain APIs.
- Lock-resource hash, refmap, dirty-list, migration, AST, and purge helpers implemented elsewhere.
- Linux kthreads, workqueues, spinlocks, wait queues, lists, and endian helpers.

## Research Notes

This file defines the distributed recovery protocol for the OCFS2 DLM. Its correctness relies on strict state transitions and conservative fatal checks. The design serializes recovery cluster-wide to one dead node at a time, uses a special DLM lock for master election, and reconstructs authoritative lock-resource state on the selected recovery master before releasing normal DLM activity.
