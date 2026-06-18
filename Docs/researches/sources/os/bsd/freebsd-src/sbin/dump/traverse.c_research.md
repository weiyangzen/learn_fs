# File Research: sources/os/bsd/freebsd-src/sbin/dump/traverse.c

Implements UFS inode traversal, dump map generation, inode serialization, block emission, extended attribute dumping, and disk read recovery.

Key responsibilities:
- `mapfiles()` scans allocated inodes, marks used inodes, directories, and changed inodes to dump.
- `mapdirs()` repeatedly prunes or adds directories based on whether they contain dumped files/subdirectories and propagates `UF_NODUMP`.
- `dumpino()` emits one inode and its file data or special-file metadata.
- `dmpindir()`, `ufs1_blksout()`, and `ufs2_blksout()` walk direct and indirect block trees and emit tape block maps.
- `appendextdata()` and `writeextdata()` append or separately emit UFS2 extended attribute data.
- `dumpmap()` writes inode maps as dump records.
- `writeheader()` fills dump protocol checksums and writes control records.
- `getino()` caches inode blocks and returns UFS1/UFS2 dinodes.
- `blkread()` reads filesystem blocks with recovery from short/hard errors.

Important macros:
- `DIP` / `DIP_SET`: abstract UFS1 versus UFS2 inode field access.
- `CHANGEDSINCE` and `WANTTODUMP`: incremental-dump selection with optional `UF_NODUMP` handling.
- `HASDUMPEDFILE` / `HASSUBDIRS`: directory search results.

Pass behavior:
- Pass I maps changed files and all directories, estimating tape blocks.
- Pass II repeats directory analysis until no parent/child inclusion changes remain.
- Pass III and IV are driven from `main.c` using maps produced here.

UFS details:
- Supports UFS1 and UFS2 inode layouts.
- Handles sparse files by clearing absent blocks in `spcl.c_addr`.
- Snapshot files are dumped as zero-length files and have `SF_SNAPSHOT` stripped in the dumped metadata.
- Root inode is always forced into `dumpinomap` because restore expects it.

Read recovery:
- `blkread()` handles non-sector-aligned reads by reading whole sectors and copying subranges.
- After repeated failures it asks the operator whether to continue, then retries sector-by-sector with zero-filled fallback data.

Risks and constraints:
- Deeply tied to FFS/UFS on-disk layout and dump protocol constants.
- `appendextdata()` contains a suspicious address test `&dp->dp2.di_extb[...] != 0`, which is always true for valid `dp`; this appears inherited and effectively marks ext blocks present based on address rather than block value.
- Error recovery may continue with zero-filled sectors, producing a restorable but incomplete dump.
