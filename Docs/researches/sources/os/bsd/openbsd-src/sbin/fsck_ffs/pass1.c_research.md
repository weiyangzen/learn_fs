# File Research: sources/os/bsd/openbsd-src/sbin/fsck_ffs/pass1.c

## Scope

Phase 1 for `fsck_ffs`: scans allocated inodes, validates inode type/size/block layout, records file and block usage, builds per-inode state, detects bad and duplicate blocks, and records zero-link-count allocated inodes.

## Main APIs

- `pass1()` reserves filesystem metadata blocks in `blockmap`, allocates `inostathead` entries per cylinder group, iterates initialized inode ranges, and calls `checkinode()`.
- `checkinode()` validates one inode, sets inode state/type, caches directories, walks blocks through `ckinode()`, and repairs incorrect `di_blocks`.
- `pass1check()` is the block callback used by `ckinode()` to validate ranges, set allocation bits, count used blocks, and populate duplicate-block lists.

## Control Flow

The pass first marks reserved superblock/cylinder-summary areas used. It then walks cylinder groups, sizes inode-state allocation from `cg_initediblk` for UFS2 or `fs_ipg` for UFS1, and scans each inode at or above `ROOTINO`.

`checkinode()` treats mode zero with nonzero block/size data as a partially allocated inode and offers to clear it. Allocated inodes are rejected if file size exceeds kernel/filesystem limits, directories exceed `MAXDIRSIZE`, file type is invalid, direct block pointers exist beyond computed size, or indirect pointers exist beyond expected depth. Directories are cached for later phases; normal files are marked `FSTATE`; bad/unknown inodes can become `FCLEAR`.

`pass1check()` rejects out-of-range fragments, caps excessive bad and duplicate reports, inserts duplicates into `duplist`/`muldup`, and increments `id_entryno` so final block count can be compared to `di_blocks`.

## Dependencies

- Relies on inode access helpers `getnextinode()`, `ginode()`, `freeinodebuf()`, `cacheino()`, `ckinode()`, `clearinode()`, and `inodirty()`.
- Uses global block map helpers `setbmap()`, `testbmap()`, `chkrange()`.
- Uses `MAXBAD` and `MAXDUP` thresholds to prevent runaway diagnostics.

## Risks And Edge Cases

- Fast symlink handling fakes `ndb` so garbage block pointers after inline symlink contents are detected.
- Link counts less than or equal to zero are not immediately cleared; they are queued in `zlnhead` for pass 4.
- Duplicate tracking distinguishes first duplicate occurrences from later repeated reports using `muldup`.
