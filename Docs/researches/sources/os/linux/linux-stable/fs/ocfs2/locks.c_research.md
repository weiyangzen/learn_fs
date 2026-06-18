# File Research: sources/os/linux/linux-stable/fs/ocfs2/locks.c

Purpose: implements OCFS2 userspace file locking hooks for BSD flock and POSIX locks, bridging Linux VFS locks to OCFS2 cluster file locks and plocks.

Read coverage: complete file read, 125 lines.

Major logic:
- `ocfs2_do_flock()` maps exclusive flock requests to OCFS2 file-lock level 1 and shared requests to level 0, converts nonblocking commands into trylock mode, serializes on `fp_mutex`, handles existing OCFS2 flock lock conversion by unlocking first, takes the cluster file lock, and then applies the VFS flock.
- If VFS flock setup fails after cluster locking, it releases the OCFS2 file lock.
- `ocfs2_do_funlock()` serializes unlock, drops the OCFS2 file lock, then applies the VFS unlock.
- `ocfs2_flock()` rejects non-flock requests, uses local VFS-only locks when mounted with local flocks or local mode, otherwise dispatches lock/unlock through OCFS2 cluster flock handling.
- `ocfs2_lock()` rejects non-POSIX locks and forwards POSIX locks to the cluster plock layer using the inode block number as resource identity.

Important entry points:
- `ocfs2_flock()`.
- `ocfs2_lock()`.

Concurrency and lifetime:
- Flock operations serialize per open file through `struct ocfs2_file_private::fp_mutex`.
- Cluster locks and VFS locks are coordinated so local VFS state is not installed unless the OCFS2 cluster lock succeeds.
- POSIX locks use the cluster connection plock service rather than the flock lock resource.

Important dependencies:
- Uses OCFS2 file lock helpers (`ocfs2_file_lock()`, `ocfs2_file_unlock()`), DLM/plock glue, file-private state, inode private block numbers, and Linux filelock APIs.

Risk and edge cases:
- Flock conversion is not atomic; the code intentionally unlocks the old level before locking the new level.
- Nonblocking flock maps `-EAGAIN` to `-EWOULDBLOCK`.
- Local flock mount option bypasses cluster flocking, which is correct only when users accept local-only lock semantics.
