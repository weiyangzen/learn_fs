# File Research: sources/local-fs/gfs2-utils/gfs2/mkfs/main_jadd.c

This file implements the `gfs2_jadd` command for adding journals to a mounted GFS2 filesystem.

Main behavior:
- Parses options for journal count, journal size, quota-change size, quiet/debug, help, and version.
- Opens and verifies a mounted GFS2 filesystem.
- Mounts GFS2 metafs and builds paths for `new_inode`, `per_node`, and `jindex`.
- Counts existing journals in `jindex`.
- Checks available filesystem space for each new journal's inum-range, statfs-change, quota-change, and journal file.
- For each new journal number:
  - Creates an `inum_rangeN` file via `new_inode`, marks it journaled data, writes zero structure, fsyncs, renames into `per_node`.
  - Creates a `statfs_changeN` file similarly.
  - Creates a `quota_changeN` file, writes quota-change metadata blocks, fsyncs, renames into `per_node`.
  - Creates `journalN`, allocates/fills journal space, finds physical block addresses with FIEMAP, writes log headers with hash/CRC, fsyncs, and renames into `jindex`.

Important helpers:
- `set_flags()` wraps `FS_IOC_GETFLAGS`/`FS_IOC_SETFLAGS`.
- `create_new_inode()` uses metafs `new_inode`.
- `find_block_address()` uses `FS_IOC_FIEMAP`.
- `alloc_new_journal()` prefers `fallocate()` and falls back to zero writes.
- `check_fit()` estimates required block count using `lgfs2_space_for_data()`.

Integration role:
- Uses mounted GFS2 metafs rather than raw block allocation.
- Uses libgfs2 constants, log hash/CRC helpers, and filesystem sizing helpers.

Risk notes:
- Directly creates system files in metafs; rename ordering is the safety boundary.
- FIEMAP must return exactly one mapped extent for each journal block lookup.
- Journal log headers rely on correct physical block addresses and CRC/hash values.
- `decode_arguments()` debug output prints `sdp->md.journals`, not `opts->journals`.
- Error paths can leave temporary `new_inode` or partially renamed system files.
