# File Research: sources/os/linux/linux/fs/vboxsf/utils.c

## Purpose
Provides vboxsf utility functions for inode allocation/initialization, host stat/revalidation, setattr/getattr, path and character-set conversion, directory-buffer management, volume property query, and file attribute reporting.

## Main Functions
- Inodes:
  - `vboxsf_new_inode()`: allocates a VFS inode and assigns cyclic IDR inode number/generation.
  - `vboxsf_init_inode()`: maps SHFL metadata to VFS mode, ops, uid/gid, size, blocks, and timestamps.
- Host stat/revalidation:
  - `vboxsf_create_at_dentry()`, `vboxsf_stat()`, `vboxsf_stat_dentry()`: lookup/stat host objects.
  - `vboxsf_inode_revalidate()`: TTL/force-based restat; reinitializes inode and invalidates pagecache when mtime increases.
- VFS attributes:
  - `vboxsf_getattr()`: handles statx sync flags and fills attributes.
  - `vboxsf_setattr()`: opens host object for attribute write, separately sets mode/times and size, closes handle, and restats.
  - `vboxsf_fileattr_get()`: reports casefold flags for case-insensitive host shares.
- Paths and NLS:
  - `vboxsf_path_from_dentry()`: converts a Linux dentry path to an aligned UTF-8 `shfl_string`.
  - `vboxsf_nlscpy()`: converts host UTF-8 names to mounted NLS encoding.
- Directory cache helpers:
  - `vboxsf_dir_info_alloc()` / `vboxsf_dir_info_free()`.
  - `vboxsf_dir_read_all()`: loops host directory listing into 16 KiB buffers.
- Host volume:
  - `vboxsf_query_case_sensitive()`: queries host volume properties and stores case-insensitive state.

## Important Design Points
- Inode modes are synthesized from host mode plus mount `dmode`/`fmode` and masks.
- `S_NOATIME | S_NOCMTIME` are set because timestamps come from the host.
- Revalidation uses dentry `d_time` plus mount TTL unless `force_restat` is set.
- Pagecache invalidation is mtime-based and can be triggered by guest writes as well as host writes.
- `setattr()` handles file size separately from other file info because the host API requires separate information modes.
- Directory read treats positive end-of-dir and `-EILSEQ` as non-fatal completion.

## Cross-File Relationships
- Used by `dir.c`, `file.c`, and `super.c`.
- Calls wrappers in `vboxsf_wrappers.c`.
- Uses ABI definitions from `shfl_hostintf.h` through `vfsmod.h`.

## Risks / Review Notes
- Host-side mutation detection is best-effort and mtime-based.
- Path conversion must fit within `PATH_MAX` minus SHFL header and NUL.
- `vboxsf_setattr()` ignores ctime because userspace cannot set it directly.
- IDR inode number wrap increments generation; consumers must tolerate synthetic inode identities.
