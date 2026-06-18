# File Research: sources/os/linux/linux-stable/fs/xfs/scrub/nlinks_repair.c

This file repairs inode link counts using the live observation data collected by `nlinks.c`.

Setup:
- `xrep_setup_nlinks` tries to create or attach `/lost+found` through orphanage support. Failure modes such as missing orphanage or ENOSPC are tolerated by the wrapper in `orphanage.h`.

Repair flow:
- `xrep_nlinks` requires `ftype`; without file types it cannot reliably repair child directory link counts.
- It walks all allocated inodes with a comparison `iscan`, skipping busy inodes so repair can make partial forward progress.
- For each inode, it cancels the scrub transaction and calls `xrep_nlinks_repair_inode`, which creates the exact transaction reservation needed for either simple nlink repair or orphanage adoption.

`xrep_nlinks_repair_inode` handles:
- Ignoring temporary repair files.
- Optionally locking `/lost+found` and the target and allocating an adoption transaction.
- Loading the observed `struct xchk_nlink` under `xnc->lock`.
- Rejecting unfixable non-directories that appear to have children.
- Moving orphaned linked files into `/lost+found` if they have no observed parents and are not roots/internal/orphanage files.
- Removing linked files from the unlinked list.
- Adding unlinked files with zero observed links to the unlinked list.
- Setting `i_nlink` to the observed total, capped at `XFS_NLINK_PINNED`.
- Logging dirty inode core state and committing the repair transaction.

The repair intentionally re-reads observations after adoption, because adoption itself updates directory entries and therefore the live nlink shadow counters.

The file coordinates with:
- `orphanage.c` for reparenting.
- `xfs_iunlink`/`xfs_iunlink_remove` for unlinked-list consistency.
- `xchk_nlink_total` for final count computation.
