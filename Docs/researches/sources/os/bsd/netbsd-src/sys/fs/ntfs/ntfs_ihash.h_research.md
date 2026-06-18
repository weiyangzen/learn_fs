# File Research: sources/os/bsd/netbsd-src/sys/fs/ntfs/ntfs_ihash.h

Private kernel header for NTFS ntnode hash support.

Key contents:
- Rejects non-kernel inclusion.
- Declares `ntfs_hashlock`.
- Declares hash lifecycle and operations:
  - init, reinit, done
  - lookup/get
  - insert/remove

Note:
- The header declares `ntfs_nthashget()`, but this grouped file set only includes an implementation for lookup/insert/remove; no `ntfs_nthashget()` body appears in `ntfs_ihash.c`.
