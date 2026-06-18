# File Research: sources/os/bsd/freebsd-src/sys/fs/tarfs/tarfs_subr.c

Tarfs support routines for sysctl tuning, node lookup/allocation/freeing, sparse block-map loading, file reads through sparse maps, and tar file flag parsing.

Key responsibilities:
- Defines malloc types for tarfs names and sparse block maps.
- Creates `vfs.tarfs` sysctl node, tunable `vfs.tarfs.ioshift`, and optional debug mask sysctl.
- Clamps preferred I/O shift between tar block size and page size, with zero mapping back to the default.
- Implements directory name lookup using the node's child `TAILQ`, with hard-link following for regular nodes whose `other` pointer is set.
- Implements directory cookie lookup with a one-entry readdir cache and a linear scan by inode cookie.
- Allocates nodes for directories, symlinks, regular files, FIFOs, block devices, and character devices, initializing attributes, generation, timestamps, block maps, names, parent links, and all-node list membership.
- Maintains parent directory contents, sizes, and link counts when inserting child nodes.
- Loads GNU sparse file block maps stored in file data: reads map blocks, parses entry count and offset/length pairs, validates alignment, ordering, and physical/logical bounds, and replaces the dummy block map.
- Frees nodes with type-specific cleanup for hard-link targets, parent directory references, symlink target buffers, names, block maps, and allocated inode numbers.
- Implements sparse-aware file reads by copying zeroes for holes and delegating actual data extents to `tarfs_io_read()`.
- Parses comma-separated file flags such as `nodump`, `uchg`, `uappnd`, `opaque`, `arch`, `schg`, and related names for PAX `SCHILY.fflags`.

Dependencies:
- Tarfs structures from `tarfs.h`, debug macros, kernel malloc, vnode/mount/namei types, sysctl, timestamps, `zero_region`, UIO, and inode number allocator APIs.
- `tarfs_io_read_buf()` and `tarfs_io_read()` for reading sparse maps and file content.

Notable risks:
- Sparse map parsing reads incrementally until enough newlines are present; malformed maps must not trigger unbounded allocation beyond the archive member size.
- The map parser uses signed `strtol()` into `long` before assigning offsets/lengths; overflow and negative values are rejected but remain sensitive to host limits.
- `tarfs_read_file()` must correctly advance both caller `uio` and local residuals across holes and data extents.
- Node freeing uses link counts to avoid freeing hard-linked data early; incorrect link accounting can leak or double-free nodes.
