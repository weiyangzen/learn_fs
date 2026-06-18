# File Research: sources/os/linux/linux-stable/fs/ceph/locks.c

## Role

`locks.c` implements CephFS POSIX byte-range locks and BSD flock locks by coordinating VFS local lock state with MDS-distributed lock state. It also serializes local locks into Ceph wire-format lock records for reconnect/reclaim style workflows.

## Lock Owner Encoding

A static `lock_secret` is initialized by `ceph_flock_init()` using `get_random_bytes()`.

`secure_addr()` xors the lock owner pointer with `lock_secret` and sets the high bit. The high bit tells the MDS that the encoded owner is sufficient to identify the lock owner, unlike older code that used owner plus pid.

## File Lock Lifetime Hooks

`ceph_fl_copy_lock()` installs private Ceph lock ownership tracking by incrementing `ci->i_filelock_ref` and storing an inode reference in `fl->fl_u.ceph.inode`.

`ceph_fl_release_lock()` releases that inode reference without using `fl_file`, which may already be gone. When the last file lock reference drops, it clears `CEPH_I_ERROR_FILELOCK` under `i_ceph_lock`.

`ceph_fl_lock_ops` wires these functions into VFS file lock lifecycle callbacks.

## MDS Lock Messaging

`ceph_lock_message()` builds and submits `CEPH_MDS_OP_SETFILELOCK` or `CEPH_MDS_OP_GETFILELOCK`.

It:

- Installs Ceph file lock ops and increments lock ref count for set-lock requests.
- Disables waiting for unlock and non-set operations.
- Creates an MDS request against the auth MDS.
- Converts VFS `[start,end]` to Ceph start/length, with length `0` representing through EOF.
- Encodes rule, type, owner, pid, start, length, and wait flag.
- Submits and waits for the request, optionally using an interrupt-aware wait helper.
- Decodes `GETFILELOCK` replies back into VFS `file_lock` fields, including negative pid convention.

## Interruptible Blocking Locks

`ceph_lock_wait_for_completion()` handles interrupted blocking lock acquisition.

If interrupted before result:

- Marks the original request aborted under `r_fill_mutex` to avoid concurrent fill paths that depend on caller-held locks.
- If the request was not yet sent, it treats the interruption as complete.
- Otherwise it sends a lock interrupt request using `CEPH_LOCK_FCNTL_INTR` or `CEPH_LOCK_FLOCK_INTR` with unlock type.
- Waits for safe completion so server-side state is settled.

This prevents orphaned distributed locks after local signal interruption.

## POSIX Lock Entry Point

`ceph_lock()` implements fcntl locking.

Behavior:

- Requires `FL_POSIX`, otherwise returns `-ENOLCK`.
- Rejects shutdown inodes with `-ESTALE`.
- Converts `GETLK`, `SETLK`, and `SETLKW` to MDS op/wait semantics.
- If `CEPH_I_ERROR_FILELOCK` is set, unlock still updates local lock state, but other operations return `-EIO`.
- Converts VFS lock type to Ceph shared/exclusive/unlock.
- For unlock, `try_unlock_file()` first checks/removes local lock state and avoids unnecessary MDS traffic when no local lock exists.
- Sends the distributed lock request.
- On successful non-unlock set-lock, installs the local POSIX lock via `posix_lock_file()`.
- If local lock installation fails, sends an MDS unlock to undo the distributed lock.

## Flock Entry Point

`ceph_flock()` is the BSD flock equivalent.

Behavior mirrors `ceph_lock()` but requires `FL_FLOCK`, uses `CEPH_LOCK_FLOCK`, always sends `CEPH_MDS_OP_SETFILELOCK`, and installs local locks with `locks_lock_file_wait()`.

On local installation failure after successful MDS lock acquisition, it sends a distributed unlock to roll back.

## Unlock Optimization

`try_unlock_file()` temporarily sets `FL_EXISTS` and calls `locks_lock_file_wait()`.

- If the VFS reports `-ENOENT` and the caller did not originally set `FL_EXISTS`, unlock is treated as success without MDS traffic.
- Otherwise a positive return tells the caller to send the MDS unlock.

## Lock Counting And Encoding

`ceph_count_locks()` counts current POSIX and flock locks from `locks_inode_context()` under `ctx->flc_lock`.

`lock_to_ceph_filelock()` converts a VFS `file_lock` to `struct ceph_filelock`, including start, length, pid, secure owner, and Ceph lock type.

`ceph_encode_locks_to_buffer()` serializes current locks into a caller-provided `struct ceph_filelock` array. It separately validates that observed fcntl/flock counts do not exceed expected counts and returns `-ENOSPC` if they do.

`ceph_locks_to_pagelist()` appends lock metadata to a `ceph_pagelist` in this order:

1. fcntl lock count
2. fcntl lock records
3. flock lock count
4. flock lock records

## Concurrency And State

- `ci->i_ceph_lock` protects `CEPH_I_ERROR_FILELOCK`.
- `i_filelock_ref` tracks active lock references and controls when filelock error state can be cleared.
- VFS lock context spinlock protects traversal of local lock lists.
- MDS request completion paths coordinate with `r_fill_mutex` on interruption to avoid racing reply-fill logic.

## Error Handling

- Nonmatching lock classes return `-ENOLCK`.
- Shutdown inodes return `-ESTALE`.
- Filelock error state returns `-EIO` except unlock still cleans local state.
- Local lock deadlock/failure after MDS success triggers best-effort MDS unlock rollback.
- Encoding unknown VFS lock types returns `-EINVAL`.
- Encoding more locks than expected returns `-ENOSPC`.
