# File Research: sources/os/bsd/openbsd-src/sbin/growfs/growfs.c

## Scope

Offline FFS filesystem grower. It expands an unmounted clean FFS partition to a larger disklabel/user-specified size, updates superblock geometry, creates or expands cylinder groups, moves cylinder-summary storage when needed, relocates occupied blocks, rewrites references, and updates the disklabel.

## Main APIs

- `main()` parses `-N`, `-q`, `-s size`, `-v`, `-y`, opens devices, validates disklabel/partition/superblock, computes new geometry, confirms backup, and calls `growfs()`.
- `growfs()` coordinates the grow operation and writes summaries, superblocks, and backups.
- `initcg()` creates new cylinder groups.
- `updjcg()` expands the former last cylinder group.
- `updcsloc()` expands or relocates cylinder-summary storage.
- `updrefs()` and `indirchk()` walk inode direct and indirect block references to update relocated data blocks.
- Low-level helpers: `rdfs()`, `wtfs()`, `alloc()`, `isblock()`, `clrblock()`, `setblock()`, `ginode()`, `frag_adjust()`, `cond_bl_upd()`, `updclst()`, disklabel helpers, and `ffs1_sb_update()`.

## Control Flow

`main()` opens the raw device for read and write unless dry-run `-N`, reads the disklabel, verifies an FFS partition, reads a valid UFS1/UFS2 superblock, requires a clean filesystem, rejects active snapshots unless expert `-y`, confirms backup, probes the final sector, computes new `fs_size`, `fs_ncg`, `fs_ncyl`, `maxino`, and expanded `fs_cssize`, then runs the grow.

`growfs()` reads old cylinder summaries, updates the old last cylinder group, initializes all newly added groups, then calls `updcsloc()` to handle cylinder-summary growth. It writes the expanded summary area, writes the new primary superblock dirty, sanitizes dynamic fields for backup copies, and writes duplicate superblocks for all cylinder groups.

`updcsloc()` either relocates the entire cylinder-summary area to a new cylinder group when the original group lacks enough free blocks, or grows it in place. In-place growth may consume blocks currently holding data; those blocks are copied to newly allocated blocks, then every allocated directory/regular-file/non-fast-symlink inode and indirect block is scanned so references to old fragments are rewritten.

## Dependencies

- FFS/UFS layout macros and on-disk structures.
- Disklabel ioctls `DIOCGDINFO` and `DIOCWDINFO`.
- `opendev()` from `libutil`.
- Uses `arc4random()` to initialize generation numbers for new inodes.

## Risks And Edge Cases

- The file explicitly notes incomplete snapshot copy-on-write support; normal mode refuses active snapshots unless `-y`.
- Dry-run `-N` cannot simulate some later relocation paths because it would need data just written to new cylinder groups.
- Cylinder-summary relocation has two strategies with different compatibility implications; moving it to a new group may require fsck versions aware of nonstandard summary placement.
- Reference updates only scan directory, regular file, and non-fast-symlink blocks, matching where block pointers are expected.
- After growing, the filesystem is intentionally marked dirty so fsck should be run.
