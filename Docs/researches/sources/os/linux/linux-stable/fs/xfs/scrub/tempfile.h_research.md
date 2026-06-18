# File Research: sources/os/linux/linux-stable/fs/xfs/scrub/tempfile.h

Declares online-repair tempfile helpers.

Key API:
- Tempfile lifecycle: `xrep_tempfile_create`, `xrep_tempfile_rele`, `xrep_is_tempfile`.
- Directory-tree adjustment: `xrep_tempfile_adjust_directory_tree`.
- Locking: IOLOCK/ILOCK nowait, polled, lock, unlock, and lock-both helpers.
- Data preparation: `xrep_tempfile_prealloc`, `xrep_tempfile_copyin`, `xrep_tempfile_set_isize`, `xrep_tempfile_roll_trans`, `xrep_tempfile_copyout_local`.
- `xrep_tempfile_copyin_fn` lets repair code fill each mapped buffer during copy-in.

Disabled configuration:
- Without online repair, most helpers disappear; `xrep_tempfile_iolock_both` falls back to locking the scrub target inode, `xrep_is_tempfile` is false, and release/adjustment are no-ops.
