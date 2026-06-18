# File Research: sources/os/bsd/netbsd-src/lib/libquota/quota_oldfiles.c

This file implements direct access to old UFS/FFS quota1 files and fstab quota-option discovery. It keeps a process-global parsed fstab table of mountpoints with `userquota` and/or `groupquota` options, including optional explicit quota-file paths.

`__quota_oldfiles_load_fstab` parses `_PATH_FSTAB` once, skipping missing fstab silently, and records only `ffs` and `lfs` entries with quota options. `__quota_oldfiles_getquotafile` returns the explicit configured quota file or constructs the default `<mountpoint>/<QUOTAFILENAME>.<type>` path using `INITQFNAMES`. `__quota_oldfiles_initialize` opens configured user/group quota files read-write, falling back to read-only for `EACCES` or `EROFS`, and stores fds on the quota handle.

The `dqblk` conversion helpers map legacy quota1 limits, usage, and times to `quotaval`. Limit zero means `QUOTA_NOLIMIT`; otherwise limits are stored as value minus one. Default quota id records use position zero and map grace through expire-time fields. Id zero is treated specially: get suppresses limits/times, and put updates usage while preserving limits/times.

`__quota_oldfiles_doget` reads one `struct dqblk` at `id * sizeof(dqblk)` or position zero for the default id, validates complete reads, converts either block or file object values, and can report all-zero records for cursor skipping. `__quota_oldfiles_doput` reads or creates a blank record, merges object-specific updates, and writes the full dqblk back. Delete clears values through `quotaval_clear`.

`__quota_oldfiles_quotaon` closes direct fds, calls the kernel quotaon path, and switches the handle to kernel mode after success. The oldfiles cursor iterates users then groups, default entry then numeric ids, blocks then files, skipping all-zero records except at the effective end to avoid false failures. One caveat visible in `cursor_create`: it calls `fstat` on both handle fds without checking that disabled user/group fds are negative, so the caller's initialization/path selection matters.
