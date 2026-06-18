# File Research: sources/os/linux/linux/fs/afs/dynroot.c

## Purpose
Implements the AFS dynamic root directory, where the root exposes known AFS cells as synthetic automount directories and exposes `@cell` / `.@cell` symlinks for the workstation cell.

## Main Responsibilities
- Creates pseudo inodes for dynroot, autocell mount directories, and `@cell` symlinks via `iget5_locked()`.
- Resolves dynroot path lookups to cells with `afs_lookup_cell()`, using dotted names as read/write volume selectors.
- Provides dynroot dentry operations, including automount dispatch through `afs_d_automount()`.
- Implements `readdir` for dynroot by walking `net->cells_dyn_ino` and emitting both undotted and dotted cell entries.

## Key Functions and Data
- `afs_dynroot_iget_root()` creates the synthetic root inode with `afs_dynroot_inode_operations` and `afs_dynroot_file_operations`.
- `afs_dynroot_lookup()` handles `@cell`, `.@cell`, and general cell-name lookup.
- `afs_dynroot_lookup_cell()` creates pseudo automount directories backed by looked-up cells.
- `afs_atcell_get_link()` resolves `@cell` and `.@cell` symlink targets from `net->ws_cell`.
- `afs_dynroot_readdir_cells()` emits active cells under the dynamic root.

## Important Details
- Pseudo inode numbers reserve `1` for root, `2`/`3` for `@cell`/`.@cell`, and then cell entries from `cell->dynroot_ino`.
- Dotted cell names use `cell->name - 1`, relying on cell names being allocated with a leading dot slot.
- `afs_dynroot_delete_dentry()` keeps only `@cell` symlink dentries around; synthetic cell dirs are dropped when unused.
- Dynamic root directories and autocell directories are read-only, no-atime pseudo directories.
