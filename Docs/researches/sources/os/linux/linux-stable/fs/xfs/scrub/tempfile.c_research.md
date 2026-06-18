# File Research: sources/os/linux/linux-stable/fs/xfs/scrub/tempfile.c

Implements hidden temporary files used to stage reconstructed metadata for online repair.

Key behavior:
- `xrep_tempfile_create` creates an unlinked, unlinkable temporary inode rooted at the filesystem root, root-owned for quota purposes, marked private, and placed on the unlinked list so recovery/inactivation can purge it.
- Directory tempfiles are initialized with `xfs_dir_init`; symlink tempfiles get a minimal valid `.` target.
- `xrep_tempfile_adjust_directory_tree` converts eligible tempfiles into metadata-directory inodes when the scrub target lives in the metadata directory tree, including quota detachment/accounting changes.
- `xrep_tempfile_remove_metadir` reverses metadata-directory state before release so inactivation follows the normal path.
- Provides IOLOCK/ILOCK helpers for tempfiles, including nowait and polled acquisition to avoid deadlocks when another inode is already locked.
- `xrep_tempfile_prealloc` ensures a tempfile range is backed by written, zeroed extents and rejects holes/delalloc surprises.
- `xrep_tempfile_copyin` walks preallocated file blocks, obtains metadata buffers, lets a caller fill each buffer, queues delayed writes, and flushes periodically.
- `xrep_tempfile_set_isize` updates disk/VFS size and rolls the repair transaction.
- `xrep_tempfile_roll_trans` logs the tempfile and rejoins it after rolling.
- `xrep_tempexch_*` helpers prepare exchange requests, estimate reservation needs, reserve blocks/quota, lock inodes, perform mapping exchange, and keep incore sizes synchronized when sizes are exchanged.
- `xrep_tempfile_copyout_local` copies local-format fork data from tempfile to target when an exchange is unnecessary or impossible.
- `xrep_is_tempfile` identifies repair tempfiles via private inode state or, for metadata-directory files, the temporary `XFS_IRECOVERY` marker.

Important constraints:
- Tempfiles must not escape to userspace.
- Atomic exchange is the commit mechanism for file-based metadata rebuilds because tempfile contents can disappear via unlinked-list cleanup.
- Quota reservation for exchanges accounts for both net and gross mapped-block movement.
