# File Research: sources/os/bsd/openbsd-src/sbin/newfs/mkfs.c

Purpose: Back-end FFS filesystem constructor used by `newfs.c`. It computes FFS1/FFS2 layout, initializes cylinder groups, creates the root directory, writes superblocks and summary information, and supports memory filesystem creation.

Inputs:
- Uses globals set by `newfs.c`: `mfs`, `Nflag`, `Oflag`, `fssize`, `sectorsize`, `fsize`, `bsize`, `maxfrgspercg`, `minfree`, `opt`, `density`, `maxbpg`, average file hints, and `membase`.
- `mkfs()` receives target partition, device name, read/write fds, and MFS root ownership/mode.

Layout computation:
- Validates filesystem size, block size, fragment size, sector size, and power-of-two requirements.
- Initializes superblock fields for FFS1 or FFS2, including inode size, indirect count, max symlink length, superblock location, masks, shifts, max file size, and compatibility geometry fields.
- Computes fragments per cylinder group and inodes per group from density, then adjusts to keep cylinder group maps within one filesystem block and to keep the last cylinder group viable.
- Computes summary block location/size, free block/free fragment/free inode totals, filesystem IDs, clean state, and optimization fields.

Write sequence:
- Writes an invalid/bad magic superblock early, then later writes the real magic after layout is established.
- For FFS2, checks for and invalidates an old FFS1 superblock at `SBLOCK_UFS1`.
- Allocates an I/O buffer containing backup superblock, cylinder group map, and initial inode blocks.
- Iterates all cylinder groups through `initcg()`, writing backups and initialized inode generation values.
- In `-N` dry-run mode, prints layout but skips final filesystem construction and writes.

Cylinder group initialization:
- `initcg()` builds each `struct cg`, marks metadata blocks used, marks free full blocks/fragments, initializes inode bitmap, and updates per-group summaries.
- FFS1-specific rotational summary tables are still populated for compatibility.
- Cylinder group 0 reserves root and prior inodes.

Root filesystem creation:
- `fsinit1()` and `fsinit2()` create the root directory inode for FFS1 and FFS2 respectively.
- `makedir()` builds `.` and `..` directory entries in `iobuf`.
- `alloc()` allocates the first data block/fragment from cylinder group 0 and updates block/free summaries.
- `iput()` writes the root inode, updates inode bitmap, and decrements free inode counts.

I/O helpers:
- `rdfs()` and `wtfs()` read/write by DEV_BSIZE block number, or copy to/from `membase` for MFS.
- `wtfs()` is a no-op under `Nflag`.
- `isblock()`, `clrblock()`, and `setblock()` manipulate fragment bitmaps for 1/2/4/8 fragments per block.

Diagnostics:
- Prints filesystem size, cylinder group count, backup superblocks, and warns if estimated `fsck_ffs` memory use exceeds min(data-size hard limit, physical memory).
- `SIGINFO` can report current cylinder group while initializing when quiet output is used on a tty.
