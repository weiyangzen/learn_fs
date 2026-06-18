# File Research: sources/os/linux/linux-stable/fs/afs/dynroot.c

## Summary
Implements the dynamic AFS root directory. It exposes configured/known cells as pseudo directories, provides `@cell` and `.@cell` symlinks to the workstation cell, and creates automount-capable pseudo-inodes for cell traversal.

## Main Responsibilities
- Creates pseudo directory inodes for dynamic root and autocell entries.
- Looks up cell names, including dotted names for read/write volume preference.
- Provides `@cell` and `.@cell` symlink handling.
- Emits dynamic root directory entries from the cell database.
- Supplies dentry operations for dynamic root automount behavior and cache deletion policy.

## Key APIs
- `afs_dynroot_iget_root()`.
- `afs_dynroot_inode_operations`.
- `afs_dynroot_dentry_operations`.
- Internal helpers: `afs_dynroot_lookup_cell()`, `afs_lookup_atcell()`, `afs_dynroot_readdir()`.

## Important Behavior
Dynamic root lookup rejects creation and overlong names. `@cell` maps to inode 2 and `.@cell` to inode 3. Ordinary cell entries are looked up through `afs_lookup_cell()` and represented by pseudo directories whose inode numbers derive from `cell->dynroot_ino * 2 + dotted`.

`afs_atcell_get_link()` returns the current workstation cell name. For dotted symlinks it returns `cell->name - 1`, relying on the cell name allocation being NUL/dot padded for dotted display.

`afs_dynroot_readdir()` emits dot entries, optional `@cell` symlinks when a workstation cell exists, then iterates `net->cells_dyn_ino`, emitting both undotted and dotted directory names for each live cell.

## State and Synchronization
Cell enumeration and workstation-cell access use `net->cells_lock` and RCU accessors. Dynamic cell dentries keep a cell usage reference in `d_fsdata`, released by `afs_dynroot_d_release()`. Non-symlink cell autodirs are allowed to be deleted from dcache when unused.

## Risks
Pseudo inode numbers are bounded by `AFS_MAX_DYNROOT_CELL_INO`. The dotted-cell behavior depends on name storage layout outside this file. Dynamic root visibility follows in-memory cell state and can skip removing/dead cells during readdir.
