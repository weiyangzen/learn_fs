# File Research: sources/os/bsd/dragonflybsd/sys/vfs/hpfs/hpfs_alsubr.c

Source read: complete file, 888 lines.

Purpose: HPFS allocation-tree support. It maps logical file blocks to device sectors, allocates and splits allocation sectors, converts embedded allocation blocks into external allocation sectors, extends files with new extents, recursively inserts extents into allocation trees, concatenates allocation sectors, and truncates allocation trees while freeing blocks.

Key interfaces:
- `hpfs_hpbmap()` descends from an fnode allocation block through alnodes/alsecs until it finds an alleaf covering a logical block; it returns the physical sector and optional run length.
- `hpfs_allocalsec()` finds a free sector, marks it busy, creates a zeroed buffer, initializes `AS_MAGIC`, parent/self links, and an empty leaf allocation block.
- `hpfs_splitalsec()` allocates a sibling alsec and moves roughly half of the current alsec records into it.
- `hpfs_concatalsec()` tries to merge two alsecs into the first and returns `ENOSPC` when records will not fit.
- `hpfs_alblk2alsec()` moves an embedded allocation block into a newly allocated allocation sector.
- `hpfs_addextent()` grows a file allocation tree from the fnode root, converting the root to alnodes when needed.
- `hpfs_addextentr()` recursively inserts extents into the rightmost alsec and reports split alnodes back to its caller.
- `hpfs_truncatealblk()` recursively frees extents at or beyond a block number and may free entire child allocation sectors.

Implementation notes:
- Allocation favors runs near the previous physical extent end by calling `hpfs_bmlookup()` with a starting sector.
- The split path sets left-subtree last `an_nextoff` to `~0` for OS/2 compatibility.
- Truncation attempts to keep the B-tree shape and explicitly notes that it never decrements tree depth.
- Buffer writeback uses `bdwrite()` for metadata changes and `brelse()` for read-only paths.

Integration:
- Relies on bitmap helpers in `hpfs_subr.c` and on on-disk allocation macros from `hpfs.h`.
- Called by `hpfs_bmap()`, `hpfs_read()`, `hpfs_write()`, `hpfs_extend()`, and `hpfs_truncate()`.

Risks and review notes:
- The code assumes the allocation tree is well-formed and has many direct pointer arithmetic operations on on-disk records.
- Some recursive error paths release only the current buffer; previously changed bitmap state may not be rolled back if later metadata writes fail.
- Truncation preserves tree depth, so long-lived files that shrink drastically can retain unnecessary allocation-tree levels.
