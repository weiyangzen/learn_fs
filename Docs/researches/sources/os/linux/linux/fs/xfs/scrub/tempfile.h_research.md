# File Research: sources/os/linux/linux/fs/xfs/scrub/tempfile.h

This header declares the temporary-file API used by online repair.

When `CONFIG_XFS_ONLINE_REPAIR` is enabled, it exposes:
- Creation/release: `xrep_tempfile_create`, `xrep_tempfile_rele`.
- Metadata-directory adjustment: `xrep_tempfile_adjust_directory_tree`.
- IOLOCK helpers: `xrep_tempfile_iolock_nowait`, `xrep_tempfile_iolock_polled`, `xrep_tempfile_iounlock`.
- ILOCK helpers: `xrep_tempfile_ilock`, `xrep_tempfile_ilock_nowait`, `xrep_tempfile_iunlock`, `xrep_tempfile_iunlock_both`, `xrep_tempfile_ilock_both`.
- Storage prep/copy: `xrep_tempfile_prealloc`, `xrep_tempfile_copyin`.
- Size/transaction/local-fork helpers: `xrep_tempfile_set_isize`, `xrep_tempfile_roll_trans`, `xrep_tempfile_copyout_local`.
- Predicate: `xrep_is_tempfile`.

Callback type:
- `xrep_tempfile_copyin_fn`: caller-provided function to populate one tempfile buffer during copy-in.

When online repair is disabled:
- `xrep_tempfile_iolock_both` falls back to locking the scrub inode with `xchk_ilock`.
- `xrep_is_tempfile` is false.
- `xrep_tempfile_adjust_directory_tree` is success.
- `xrep_tempfile_rele` is a no-op.

Risk notes:
- The header lets scrub/repair code compile in non-repair kernels without scattering config checks through callers.
