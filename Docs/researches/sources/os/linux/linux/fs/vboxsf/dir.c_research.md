# File Research: sources/os/linux/linux/fs/vboxsf/dir.c

## Purpose
Implements vboxsf directory file operations, dentry revalidation, and directory inode operations such as lookup, create, mkdir, atomic open, unlink/rmdir, rename, and symlink.

## Main Functions
- Directory file ops:
  - `vboxsf_dir_open()`: opens the host directory, reads all entries into a cached `vboxsf_dir_info`, then closes the host handle.
  - `vboxsf_dir_release()`: frees cached directory information.
  - `vboxsf_dir_iterate()` / `vboxsf_dir_emit()`: emits cached host entries to VFS with fake inode numbers.
  - `vboxsf_get_d_type()`: maps SHFL file type bits to Linux `DT_*`.
- Dentry handling:
  - `vboxsf_dentry_revalidate()`: rejects RCU lookup, revalidates positive dentries, and confirms negative dentries still do not exist.
- Directory inode ops:
  - `vboxsf_dir_lookup()`: stats the host path and creates/initializes a new inode.
  - `vboxsf_dir_create()` and wrappers `vboxsf_dir_mkfile()` / `vboxsf_dir_mkdir()`: create files/directories on the host and instantiate dentries.
  - `vboxsf_dir_atomic_open()`: lookup/create/open path for `O_CREAT`, attaching the host handle to the file.
  - `vboxsf_dir_unlink()`: removes files, directories, or symlinks with the correct SHFL flags.
  - `vboxsf_dir_rename()`: renames host paths, replacing existing targets for files.
  - `vboxsf_dir_symlink()`: creates host symlink and instantiates the resulting inode.

## Important Design Points
- Directories are snapshotted at open time by `vboxsf_dir_read_all()`; iteration walks cached variable-length `shfl_dirinfo` records.
- Fake inode numbers are derived from `ctx->pos + 1`; overflow truncates directory iteration on 32-bit inode configurations.
- Name conversion through NLS can skip individual invalid entries rather than failing the whole directory iteration.
- Parent inodes set `force_restat` after mutations so later revalidation pulls host-updated metadata.
- `atomic_open` handles newly-created files by preserving the host handle and installing it as `file->private_data`.

## Cross-File Relationships
- Uses `vboxsf_create_at_dentry()`, `vboxsf_dir_read_all()`, `vboxsf_path_from_dentry()`, `vboxsf_stat_dentry()`, and inode helpers from `utils.c`.
- Uses host operations from `vboxsf_wrappers.c`: create, close, remove, rename, symlink.
- Publishes `vboxsf_dir_fops`, `vboxsf_dentry_ops`, and `vboxsf_dir_iops` declared in `vfsmod.h`.

## Risks / Review Notes
- Host-provided directory data is variable-sized and only bounds-checked against buffer usage; corrupt host data triggers warnings and stops emission.
- Directory snapshots can become stale if host-side changes occur after open.
- RCU path walk is unsupported for dentry revalidation.
- Rename rejects all VFS rename flags, so newer rename semantics such as exchange or noreplace are unsupported.
