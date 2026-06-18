# File Research: sources/os/linux/linux/fs/ocfs2/dlm/dlmunlock.c

## Purpose
Implements OCFS2 DLM unlock and cancel operations for local-master and remote-master lock resources, including lock queue updates, LVB updates, remote unlock messaging, and unlock AST delivery.

## Major Responsibilities
- Central unlock/cancel logic lives in `dlmunlock_common()`.
- Local and remote wrappers:
  - `dlmunlock_master()`
  - `dlmunlock_remote()`
- Remote message sender:
  - `dlm_send_remote_unlock_request()`
- Remote unlock handler:
  - `dlm_unlock_lock_handler()`
- Pending recovery helpers:
  - `dlm_commit_pending_unlock()`
  - `dlm_commit_pending_cancel()`
- Action selection:
  - `dlm_get_cancel_actions()`
  - `dlm_get_unlock_actions()`
- Public exported API:
  - `dlmunlock()`

## Unlock Semantics
- Plain unlock must target a granted lock.
- Cancel must target converting or blocked locks; canceling an already granted conversion reports `DLM_CANCELGRANT`.
- Unlock action bits control whether to remove the lock, free it, call unlock AST, regrant it, or clear convert type.
- LVB updates are accepted for valid unlock paths and copied locally for master resources or sent as extra network vector data for remote resources.

## Remote Path
- Remote unlock sends `DLM_UNLOCK_LOCK_MSG` with the lock cookie, node id, flags, name, and optional LVB.
- If the owner has become the local node due to migration, sender returns `DLM_FORWARD` so the caller retries locally.
- If the remote master is down, the call can complete as `DLM_NORMAL` once the node is known dead; otherwise `DLM_NOLOCKMGR` prompts retry.
- The remote handler validates flags/name length, finds the lock resource, verifies local mastery, locates the lock by cookie/node across granted/converting/blocked queues, applies optional LVB, and invokes master unlock logic.

## Retry Behavior
`dlmunlock()` retries on:
- `DLM_RECOVERING`
- `DLM_MIGRATING`
- `DLM_FORWARD`
- `DLM_NOLOCKMGR`

Retries sleep briefly to allow recovery, migration, or reconnect progress.

## Concurrency and Synchronization
- `res->spinlock` protects queue membership and lockres state.
- `lock->spinlock` protects lock fields such as convert type and pending flags.
- `dlm->ast_lock` is checked to avoid unlocking a lock with pending ASTs unless canceling.
- `DLM_LOCK_RES_IN_PROGRESS` serializes master operations.
- Unlock waits for recovery completion in a specific path where a remote unlock succeeds because the owner died and recovery must finish before purge is missed.

## Risks and Invariants
- Unlocking with pending ASTs is rejected as `DLM_BADPARAM`.
- Cancel and unlock queue-state expectations are strict and can trigger diagnostics.
- Some invalid states use `BUG()` because queue corruption or wrong lock ownership would break cluster correctness.
- `LKM_GET_LVB` is invalid on unlock; `LKM_PUT_LVB` with cancel is rejected.
