# File Research: sources/local-fs/ocfs2-tools/fswreck/include/corrupt.h

This header declares the top-level fswreck corruption dispatch functions implemented in `corrupt.c`.

Exports:
- Dispatchers for file, system file, group descriptor, inode, local alloc, truncate log, refcount, and discontiguous block-group corruption.
- `create_named_directory()` helper for creating root-level working directories.

Integration notes:
- Included by `main.h`.
- `corrupt_inode()` is declared here but no implementation was present in this grouped source set; main dispatch uses other corruption dispatchers directly.
