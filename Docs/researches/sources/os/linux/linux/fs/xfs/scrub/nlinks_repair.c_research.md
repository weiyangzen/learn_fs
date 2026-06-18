# File Research: sources/os/linux/linux/fs/xfs/scrub/nlinks_repair.c

## Role
Repairs inode link counts using the live shadow data collected by `nlinks.c`.

## Setup
- `xrep_setup_nlinks` tries to create/attach the orphanage (`/lost+found`) so disconnected linked inodes can be adopted.

## Repair Flow
- `xrep_nlinks` requires filetype support because accurate child directory counting depends on dirent ftypes.
- It scans all allocated inodes using a comparison iscan and calls `xrep_nlinks_repair_inode`.
- Empty transactions are used between inode repairs to avoid metadata deadlocks.

## Inode Repair
- Loads observed counts from the shared `xfarray` while holding the nlink mutex and inode locks.
- Refuses unfixable non-directories with child-directory observations.
- Orphaned linked inodes with no parents can be moved to the orphanage.
- Synchronizes the unlinked list:
  - linked inodes on the unlinked list are removed from it;
  - unlinked inodes not on the list are added.
- Updates VFS `i_nlink`, capped at `XFS_NLINK_PINNED`, and logs the inode core.

## Risk Points
- Repair is only valid if the collection scan was not aborted.
- Orphanage adoption requires careful IOLOCK/ILOCK and transaction ordering.
- Missing ftype support disables repair rather than risking wrong directory counts.
