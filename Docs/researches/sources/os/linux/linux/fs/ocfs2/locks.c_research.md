# File Research: sources/os/linux/linux/fs/ocfs2/locks.c

`locks.c` implements userspace file locking support for OCFS2.

Main responsibilities:
- Implements BSD flock handling through `ocfs2_flock()`.
  - Validates `FL_FLOCK`.
  - Falls back to local VFS locking when mounted with local flocks or in local mount mode.
  - Uses OCFS2 file-private cluster locks for clustered flock enforcement.
- `ocfs2_do_flock()` maps read/write flock requests to PR/EX-style file locks, handles trylock vs blocking semantics, serializes through `fp_mutex`, converts existing locks by unlocking first, then calls `ocfs2_file_lock()` and `locks_lock_file_wait()`.
- Converts failed nonblocking cluster lock `-EAGAIN` into `-EWOULDBLOCK`.
- `ocfs2_do_funlock()` releases the OCFS2 file lock and then updates the VFS lock state.
- Implements POSIX lock handling through `ocfs2_lock()`.
  - Validates `FL_POSIX`.
  - Delegates clustered POSIX lock management to `ocfs2_plock()` using the inode block number as the lock identity.

Key invariants:
- Cluster flock state and VFS lock state are updated under the file-private mutex.
- Local flock mount mode bypasses cluster locking.
- POSIX locks are routed through the cluster plock stack, not the flock path.
