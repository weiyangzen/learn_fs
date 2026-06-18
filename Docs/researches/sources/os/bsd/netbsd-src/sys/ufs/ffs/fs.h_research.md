# File Research: sources/os/bsd/netbsd-src/sys/ufs/ffs/fs.h

Read completely: 774 lines.

Defines the NetBSD FFS/UFS on-disk superblock, cylinder-group layout, constants, feature flags, and address/size conversion macros.

Core on-disk layout:
- Documents FFS superblock search locations: floppy/front, UFS1 at 8 KiB, UFS2 at 64 KiB, and fallback at 256 KiB, with `SBLOCKSEARCH` deliberately avoiding UFS1 probing at the UFS2 offset.
- Defines boot block and superblock constants (`BBSIZE`, `SBLOCKSIZE`), fragmentation limits (`MAXFRAG`), minimum block size (`MINBSIZE`), mount/volume name lengths, snapshot limits, and layout tuning defaults.
- `struct csum` and `struct csum_total` hold per-cylinder-group and filesystem-wide free-space/directory/inode summaries.
- `struct fs` is the FFS superblock ABI, carrying layout offsets, block/fragment geometry, cylinder group counts, derived masks/shifts, clean state, mount name, volume name, journal/quota/snapshot metadata, cylinder summaries, size fields, flags, inode format, and magic.
- `struct cg` is the modern cylinder group ABI; `struct ocg` preserves old cylinder group layout compatibility.

Feature and compatibility flags:
- Magic values cover UFS1, UFS2, UFS2 extended attributes, swapped-endian variants, and `FS_OKAY`.
- Clean flags distinguish clean and was-clean states.
- Filesystem flags include soft dependencies, WAPBL, quota2, POSIX.1e ACLs, NFSv4 ACLs, TRIM, and compatibility flags from FreeBSD/gjournal.
- `FS_SWAPPED` is the internal endian-swapped marker.

Access and layout macros:
- Cylinder-group accessors abstract old/new cg layouts and swapped-endian fields.
- Address macros map filesystem blocks to disk blocks, cylinder group bases, inode block addresses, inode offsets, block maps, rotational tables, and free-space computations.
- Fast geometry macros implement block/fragment offset, rounding, block-to-fragment conversion, logical block numbers, and direct/indirect block pointer reads for UFS1 vs UFS2.
- `ffs_blksize()` and `ffs_sblksize()` compute real file-block size for fragment-sized final blocks.
- Apple UFS label constants and packed `struct appleufslabel` describe the optional Apple label region.

Risks and notes:
- This is ABI-defining source; changing field order, constants, or macro semantics affects mount, fsck, boot, and cross-BSD compatibility.
- Comments warn that UFS2/FFSv2 superblock placement creates compatibility traps with stale UFS1/UFS2 superblocks.
- Several fields are historical, unused, or compatibility aliases, but remain part of the on-disk structure.
