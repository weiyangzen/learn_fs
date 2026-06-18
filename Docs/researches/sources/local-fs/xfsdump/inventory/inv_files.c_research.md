# File Research: sources/local-fs/xfsdump/inventory/inv_files.c

Centralizes inventory path selection and path construction.

Key behavior:
- Chooses between FHS path `/var/lib/xfsdump` and legacy `/var/xfsdump`.
- If both bases exist and are distinct filesystems/inodes, setup fails.
- Builds static paths for inventory directory, fstab file, and lock file.
- Exposes `inv_dirpath()`, `inv_fstab()`, `inv_lockfile()`, and `inv_basepath()`.

Important dependencies:
- `INV_DIRPATH`, `INV_FSTAB`, and `INV_LOCKFILE` macros in public/private headers call these functions.
- `inv_setup_base()` must be called before path access; accessors assert `inv_base` is initialized.

Notable observations:
- Uses fixed 64-byte path buffers because paths are known constants.
- Path migration logic prefers the new `/var/lib/xfsdump` base unless the old base exists.
