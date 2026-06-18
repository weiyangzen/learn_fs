# File Research: sources/os/linux/linux/fs/ocfs2/dlmfs/userdlm.c

## Purpose
Implements the DLM protocol logic behind dlmfs regular files. It manages lock acquisition, conversion, blocking AST handling, holder counts, LVB reads/writes, teardown, and cluster connect/disconnect.

## Major Responsibilities
- Defines a user-dlm locking protocol with AST, BAST, and unlock AST callbacks.
- Tracks each lock resource through `struct user_lock_res`.
- Converts userspace file opens into PR/EX DLM locks.
- Handles blocking ASTs by queuing downconversion work.
- Cancels in-flight converts when a BAST requires downconversion.
- Provides lock destruction for unlink/eviction.
- Registers and unregisters DLM domains using OCFS2 stack glue.

## State Model
Important `l_flags` bits:
- `USER_LOCK_ATTACHED`: DLM lock has been initialized and LVB is available.
- `USER_LOCK_BUSY`: DLM lock/unlock/convert operation is in flight.
- `USER_LOCK_BLOCKED`: BAST requested downconversion.
- `USER_LOCK_IN_TEARDOWN`: lock is being destroyed.
- `USER_LOCK_QUEUED`: downconversion work is queued.
- `USER_LOCK_IN_CANCEL`: cancel request is in flight.

Lock levels are intentionally limited to EX, PR, NL, and IV assumptions.

## Acquisition Flow
- `user_dlm_cluster_lock()` validates requested level.
- It waits/retries if:
  - teardown is active;
  - a higher-level operation is busy;
  - the lock is blocked and the requested level is incompatible with the pending downconvert.
- If an upconvert/acquire is needed, it sets `USER_LOCK_BUSY`, issues `ocfs2_dlm_lock()` with `DLM_LKF_VALBLK` and optional `DLM_LKF_CONVERT`, waits for AST completion, and retries.
- Once compatible, it increments EX or PR holder counts.

## Blocking and Downconversion Flow
- `user_bast()` records the highest blocking level, sets `USER_LOCK_BLOCKED`, queues work, and wakes waiters.
- `user_dlm_unblock_lock()` decides whether downconversion can proceed:
  - exits if no longer blocked or tearing down;
  - cancels a busy convert if needed;
  - waits for incompatible local holders to drain;
  - chooses the highest compatible level and issues a DLM convert with `DLM_LKF_CONVERT | DLM_LKF_VALBLK`.
- `user_ast()` completes acquire/convert, updates `l_level`, clears busy, and clears blocked when a downconvert satisfies the blocking request.
- `user_unlock_ast()` completes teardown or cancel paths and can requeue blocked work after a successful cancel.

## Unlock and Teardown
- `user_dlm_cluster_unlock()` decrements holder counts and conditionally queues downconversion when blockers can now be satisfied.
- `user_dlm_destroy_lock()` prevents new users with `USER_LOCK_IN_TEARDOWN`, waits for busy operations, refuses destruction while holders remain, and unlocks the attached DLM lock with `DLM_LKF_VALBLK`.
- A never-attached lock is simply left in teardown state and returns success.

## LVB Handling
- `user_dlm_write_lvb()` requires EX level and writes into the DLM LVB.
- `user_dlm_read_lvb()` requires PR or stronger, returns false if the LVB is invalid, otherwise copies `DLM_LVB_LEN`.
- Lock and downconvert operations use `DLM_LKF_VALBLK` so the LVB participates in DLM protocol updates.

## Cluster Glue
- `user_dlm_set_locking_protocol()` publishes the max protocol version to stack glue.
- `user_dlm_register()` calls `ocfs2_cluster_connect_agnostic()` with a no-op recovery handler.
- `user_dlm_unregister()` disconnects the cluster connection.

## Concurrency and Lifetime
- `l_lock` protects flags, levels, holder counts, requested/blocking state, and LVB access.
- `l_event` wakes waiters for busy and blocked state changes.
- Downconvert work holds an inode reference while queued/running, dropped at worker completion.
