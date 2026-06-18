# File Research: sources/os/linux/linux-stable/fs/ocfs2/dlm/dlmunlock.c

## Purpose

Implements OCFS2 DLM unlock and cancel operations for both local-master and remote-master lock resources. It validates DLM unlock semantics, updates lock queues, propagates remote unlock requests, handles recovery/migration retries, and invokes unlock AST callbacks.

## Major Responsibilities

- Enforce DLM rules for cancel versus unlock:
  - `LKM_CANCEL` applies to converting or blocked locks.
  - normal unlock applies to granted locks.
- Compute local queue/refcount actions for cancel/unlock.
- Send remote unlock/cancel messages to the lock resource master.
- Handle incoming remote unlock messages.
- Update LVB state on unlock where allowed.
- Retry across recovery, migration, forwarded mastership, and reconnect conditions.
- Coordinate unlock AST delivery and lock freeing.

## Action Flags

Internal action bits describe what the common unlock path should do:

- `DLM_UNLOCK_FREE_LOCK`
- `DLM_UNLOCK_CALL_AST`
- `DLM_UNLOCK_REMOVE_LOCK`
- `DLM_UNLOCK_REGRANT_LOCK`
- `DLM_UNLOCK_CLEAR_CONVERT_TYPE`

These are computed by `dlm_get_cancel_actions()` or `dlm_get_unlock_actions()`.

## Core Unlock Flow

`dlmunlock()` is the exported API.

It:

1. Validates arguments and flags.
2. Ignores `LKM_VALBLK` when paired with `LKM_CANCEL`.
3. Grabs references to the lock and lock resource.
4. Determines whether this node is the master.
5. Calls `dlmunlock_master()` or `dlmunlock_remote()`.
6. Retries on:
   - `DLM_RECOVERING`
   - `DLM_MIGRATING`
   - `DLM_FORWARD`
   - `DLM_NOLOCKMGR`
7. Invokes unlock AST if requested.
8. Kicks the DLM thread on successful unlock.
9. Recalculates lock-resource usage.
10. Drops references.

`DLM_CANCELGRANT` is converted to `DLM_NORMAL` before returning to callers.

## Common Local/Remote Logic

`dlmunlock_common()` handles both master and non-master cases.

It:

- Rejects normal unlock while an AST is still pending.
- Handles `DLM_LOCK_RES_IN_PROGRESS`, recovery, and migration states.
- Computes queue actions.
- Updates LVB locally if master and `LKM_VALBLK` is valid.
- For remote resources, marks `cancel_pending` or `unlock_pending`, sends a remote request, then clears or adjusts actions depending on the response.
- Applies list changes and lock refcount changes.
- Clears `DLM_LOCK_RES_IN_PROGRESS`.
- Waits for recovery completion in the special case where unlock succeeded because owner died and recovery must still purge state.
- Sets the caller’s `call_ast` flag if needed.

## Cancel Semantics

`dlm_get_cancel_actions()`:

- Blocked lock: remove it and call AST.
- Converting lock: remove from converting, regrant on granted list, clear convert type, call AST.
- Granted lock: returns `DLM_CANCELGRANT`; the cancel lost the race because the lock was already granted.
- Not on any queue: returns `DLM_IVLOCKID`.

`dlm_commit_pending_cancel()` is used by recovery cleanup to complete a pending cancel by moving the lock back to granted and clearing convert type.

## Unlock Semantics

`dlm_get_unlock_actions()`:

- Requires the lock to be on granted list.
- If not granted, returns `DLM_DENIED`.
- If granted, removes and frees the lock and calls unlock AST.

`dlm_commit_pending_unlock()` is used during recovery cleanup to treat an in-progress unlock as completed.

## Remote Unlock Request

`dlm_send_remote_unlock_request()` sends `DLM_UNLOCK_LOCK_MSG`.

It includes:

- requesting node
- flags
- lock cookie
- lock name
- optional LVB payload for `LKM_PUT_LVB`

Important outcomes:

- If owner is now local, returns `DLM_FORWARD` so caller retries locally.
- If network send reports host down and the owner is now known dead, returns `DLM_NORMAL`; recovery will complete the logical operation.
- Otherwise host-down before confirmed death maps to `DLM_NOLOCKMGR`.
- Other send errors map through `dlm_err_to_dlm_status()`.

## Remote Handler

`dlm_unlock_lock_handler()` handles incoming unlock/cancel messages on the master.

It validates:

- no `LKM_GET_LVB` on unlock
- no `LKM_PUT_LVB` with `LKM_CANCEL`
- lock name length

It then:

- Grabs the DLM context.
- Looks up the lock resource.
- Rejects/forwards if recovering, migrating, missing, or not master.
- Finds the lock by cookie and node across granted/converting/blocked queues.
- Applies optional LVB update for EX locks.
- Calls `dlmunlock_master()`.
- Recalculates usage and kicks the DLM thread.

Missing lock resources are treated as likely migrated away and return `DLM_FORWARD`.

## Concurrency

- Uses `res->spinlock` for lock-resource queues/state.
- Uses `lock->spinlock` for per-lock state.
- Uses `dlm->ast_lock` to reject unsafe unlock while ASTs are pending.
- Waits on lock-resource flags through `__dlm_wait_on_lockres_flags()`.
- Avoids sleeping while holding spinlocks around network sends.

## Dependencies

- DLM common lock resource and lock helpers.
- OCFS2 cluster network messaging.
- Recovery state helpers from `dlmrecovery.c`.
- DLM thread kick and usage recalculation from `dlmthread.c`.

## Research Notes

This file is a carefully structured state machine around lock lifetime. The remote path intentionally completes logical unlock/cancel operations when a master dies at the right time, relying on recovery to carry corrected state to the recovery master. Refcount and list operations are tightly coupled with action flags.
