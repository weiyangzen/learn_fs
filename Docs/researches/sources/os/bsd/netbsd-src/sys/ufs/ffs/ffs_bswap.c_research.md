# File Research: sources/os/bsd/netbsd-src/sys/ufs/ffs/ffs_bswap.c

This file implements byte-order conversion for FFS/UFS on-disk structures. It is used by kernel and userland tooling when reading or writing filesystems whose byte order differs from the host.

Key responsibilities:
- Swap FFS superblocks, UFS1/UFS2 dinodes, cylinder group summaries, total summaries, and cylinder groups.
- Preserve opaque bitmap/block-pointer arrays that are either endian-neutral at this layer or handled elsewhere.
- Support both old UFS1 cylinder group layouts and newer layouts with offset-based summary tables.

Important functions:
- `ffs_sb_swap`: Converts the fixed superblock fields, quota fields, snapshot inode array, summary totals, size/time fields, masks, flags, and magic. It bulk-swaps the initial contiguous 32-bit field region up to `fs_fmod`.
- `ffs_dinode1_swap`: Converts UFS1 inode metadata fields while copying direct/indirect block arrays unchanged.
- `ffs_dinode2_swap`: Converts UFS2 inode metadata, including 64-bit timestamps, birthtime, block count, extattr size, and flags; copies extattr/data/indirect block arrays unchanged.
- `ffs_csum_swap`: Swaps an arbitrary cylinder-summary byte range as 32-bit words.
- `ffs_csumtotal_swap`: Converts 64-bit aggregate directory/free-block/free-inode/free-fragment counters.
- `ffs_cg_swap`: Converts cylinder group headers, fragment summaries, old rotational tables, cluster summaries, and UFS1 block totals/position tables. It may be called in-place.

Important interactions:
- Declared in `ffs_extern.h`; called during mount, reload, snapshot writeout, and summary update paths.
- Uses `ufs_rw*`/`UFS_FSNEEDSWAP` conventions indirectly through callers.
- Must stay aligned with on-disk `struct fs`, `struct cg`, `struct ufs1_dinode`, and `struct ufs2_dinode`.

Notable behavior and risks:
- Several superblock fields overlap historic postbl table locations; the code explicitly comments on those compatibility areas.
- Dinode block pointer arrays are copied, not swapped here; consumers must interpret them through UFS byte-order helpers.
- `ffs_cg_swap` chooses offsets based on the already-converted or original magic, which is subtle but necessary for in-place use.
