# File Research: sources/os/bsd/openbsd-src/sbin/dump/traverse.c

## Purpose
Traverses UFS metadata, builds dump inclusion maps, estimates dump size, and emits inode/data records.

## Key Behavior
- Defines a `union dinode` abstraction over UFS1 and UFS2 inode formats with `DIP()` field access.
- `blockest()` estimates tape blocks for an inode, accounting for holes and indirect block overhead.
- `mapfileino()` marks allocated inodes, directories, and modified files based on mtime/ctime versus previous dump date, with `UF_NODUMP` policy.
- `fs_mapinodes()` scans cylinder groups and initialized inode ranges.
- `mapfiles()` implements pass I for full filesystems or FTS-based file/directory subsets; ensures root inode is dumped.
- `mapdirs()` implements pass II, repeatedly scanning directories to include parents needed for modified descendants and propagate nodump exclusion.
- `dirindir()` and `searchdir()` walk direct and indirect directory blocks to detect dumped children/subdirectories.
- `dumpino()` emits headers and data for directories, regular files, symlinks, device nodes, FIFOs, sockets, and empty files.
- Short symlinks stored in inode data are dumped as inline data records.
- `dmpindir()`, `ufs1_blksout()`, and `ufs2_blksout()` walk direct/indirect block pointers and emit TS_ADDR/data records.
- `dumpmap()` writes inode bitmaps to tape.
- `writeheader()` fills magic/checksum fields for UFS1/UFS2 dump headers.
- `getino()` caches one inode block and returns the requested inode.
- `bread()` performs sector-aligned reads using disklabel geometry, retries hard reads sector-by-sector, zero-fills failed regions, and asks the operator after too many errors.

## Notes
This module is tightly coupled to UFS on-disk structures and the dump tape format. It is responsible for making incremental dumps restorable by preserving directory context.
