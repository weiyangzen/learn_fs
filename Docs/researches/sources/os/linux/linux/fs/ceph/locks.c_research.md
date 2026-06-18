# File Research: sources/os/linux/linux/fs/ceph/locks.c

## Purpose

`locks.c` implements CephFS POSIX byte-range locks (`fcntl`) and BSD-style flock locks by coordinating Linux local file locks with MDS-distributed lock state. It also serializes current local lock state for cap/session recovery and reconnect paths.

## Major Interfaces

- `ceph_flock_init()` initializes a per-boot random lock secret.
- `ceph_lock()` handles POSIX/fcntl `GETLK`, `SETLK`, and `SETLKW` style locks.
- `ceph_flock()` handles flock locks.
- `ceph_count_locks()` counts current local fcntl and flock locks on an inode.
- `ceph_encode_locks_to_buffer()` converts local locks to Ceph wire-format `struct ceph_filelock` entries.
- `ceph_locks_to_pagelist()` appends encoded lock counts and arrays to a Ceph pagelist.

## Lock Owner Encoding

`secure_addr()` XORs a kernel lock-owner pointer with the random `lock_secret` and sets the top bit. This lets the MDS identify owners without exposing raw kernel addresses and tells old MDS-side logic that the owner value alone is sufficient.

## File Lock Lifetime Hooks

`ceph_fl_copy_lock()` increments `ci->i_filelock_ref` and stores an inode reference in `fl->fl_u.ceph.inode`.

`ceph_fl_release_lock()` drops that inode reference later without relying on `fl_file`, which may already be released by another thread. When the last file lock reference is gone, it clears `CEPH_I_ERROR_FILELOCK` under `i_ceph_lock`.

These hooks are installed in `ceph_fl_lock_ops`.

## MDS Lock Messaging

`ceph_lock_message()` is the common MDS request path. For `CEPH_MDS_OP_SETFILELOCK`, it preinstalls Ceph file-lock operations and increments the inode lock ref before request submission, closing a race where auth caps could be trimmed between reply handling and local lock insertion.

It converts Linux lock state into Ceph request fields:

- lock rule: fcntl or flock;
- operation: get or set lock;
- command: shared, exclusive, unlock;
- owner from `secure_addr()`;
- pid;
- start and length, with length `0` representing through EOF;
- wait flag for blocking requests.

It submits and waits for the MDS request. For `GETFILELOCK`, it converts the reply back into Linux `struct file_lock` state, including negative pid values, lock type, start, and end.

## Interruptible Blocking Locks

`ceph_lock_wait_for_completion()` handles interruptible waits for blocking set-lock requests. If interrupted before the result arrives, it marks the original request aborted under `mdsc->mutex` and `req->r_fill_mutex` when safe. If the request was already sent, it creates a separate interrupt unlock request using `CEPH_LOCK_FCNTL_INTR` or `CEPH_LOCK_FLOCK_INTR`, then waits for the original request's safe completion.

This avoids leaving an MDS-side blocking lock request active after the local waiter was interrupted.

## POSIX Lock Flow

`ceph_lock()` rejects non-POSIX locks with `-ENOLCK` and shutdown inodes with `-ESTALE`. It checks `CEPH_I_ERROR_FILELOCK`; if set, unlock requests are applied locally and the function returns `-EIO`.

For `GETLK`, it sends `CEPH_MDS_OP_GETFILELOCK`. For blocking lock commands it sets `wait = 1`. Unlock operations first call `try_unlock_file()` to remove local locks and can return early when no remote unlock is needed. Successful remote non-unlock set operations are then installed locally with `posix_lock_file()`. If local locking fails, usually due to local deadlock detection, it sends a remote unlock to undo the MDS state.

## Flock Flow

`ceph_flock()` mirrors the POSIX flow for `FL_FLOCK` locks. It rejects non-flock locks and shutdown inodes, handles `CEPH_I_ERROR_FILELOCK`, sets blocking wait state for `SETLKW`, tries local unlock first, sends `CEPH_LOCK_FLOCK` set requests to the MDS, and then installs successful non-unlock locks locally with `locks_lock_file_wait()`. If local installation fails, it sends a remote unlock.

## Lock Counting And Encoding

`ceph_count_locks()` obtains the inode's `file_lock_context`, locks `ctx->flc_lock`, and counts entries in `flc_posix` and `flc_flock`.

`lock_to_ceph_filelock()` converts a Linux lock to Ceph wire fields: start, length, client id `0`, pid, secure owner, and shared/exclusive/unlock type.

`ceph_encode_locks_to_buffer()` iterates local POSIX and flock locks under `ctx->flc_lock`, encodes them into a caller-provided array, and returns `-ENOSPC` if more locks are observed than the caller counted earlier.

`ceph_locks_to_pagelist()` writes the serialized lock format: fcntl count, fcntl lock array, flock count, flock lock array.

## Dependencies

The file depends on Linux file-lock internals, Ceph MDS request APIs, Ceph pagelists, Ceph inode cap/error flags, inode refs, and random bytes for owner obfuscation.

## Error Handling And Risks

- Remote success followed by local lock failure requires an explicit remote unlock; this code handles that rollback for both POSIX and flock paths.
- Blocking lock interruption is complex and relies on request flags, fill mutex, interrupt unlock messages, and safe completion ordering.
- `ceph_encode_locks_to_buffer()` can race with lock changes between the caller's count and encode phases; it detects overflow with `-ENOSPC`.
- `lock_to_ceph_filelock()` computes length as `fl_end - fl_start + 1`; callers must ensure lock ranges are normalized and not overflowing.
- `CEPH_I_ERROR_FILELOCK` causes new lock operations to fail until all file lock refs are released and the release hook clears the flag.

## Testing Signals

Relevant tests should cover:

- POSIX `GETLK`, nonblocking set, blocking set, unlock, and local deadlock rollback.
- Flock shared/exclusive/unlock behavior.
- Interrupted blocking locks and MDS interrupt unlock behavior.
- Session reconnect lock replay using count/encode/pagelist helpers.
- File lock error flag behavior across final lock release.
