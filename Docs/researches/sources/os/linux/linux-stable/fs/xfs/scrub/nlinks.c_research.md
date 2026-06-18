# File Research: sources/os/linux/linux-stable/fs/xfs/scrub/nlinks.c

This file implements live scrub of inode link counts for the whole XFS filesystem. Link counts are treated as summary metadata reconstructed from directory entries, parent pointers, and superblock-rooted metadata inode references.

Core flow:
- `xchk_setup_nlinks` enables directory-entry live update gates, optionally prepares repair support, allocates `struct xchk_nlink_ctrs`, and sets up a filesystem scrub.
- `xchk_nlinks_setup_scan` creates a sparse `xfarray` indexed by inode number to hold `struct xchk_nlink` observations, starts an inode scan, and installs a directory update hook.
- `xchk_nlinks_collect` first counts superblock-rooted metadata files, then walks all allocated inodes. Directories are walked with `xchk_dir_walk`; non-directories are only marked visited.
- `xchk_nlinks_compare` walks allocated inodes again to compare observed counts to actual `i_nlink`, then walks unvisited sparse observations to catch dangling references to missing or busy inodes.

The observation model separates:
- `parents`: forward directory entries pointing to an inode.
- `children`: subdirectory entries inside a directory, plus directory dot semantics through `xchk_nlink_total`.
- `backrefs`: child directory `..` references or parent-pointer references pointing back to a directory.

Live update behavior:
- `xchk_nlinks_live_update` hooks directory updates after an inode or directory has already been scanned.
- Updates are guarded by `xnc->lock`.
- Hook errors abort `collect_iscan`; the scrubber later converts this into `INCOMPLETE`.
- Temporary repair directories are ignored because their staged contents do not maintain normal child link counts.

Important invariants checked:
- `.` must point to the containing directory.
- Directory names and inode numbers must verify.
- Directories with zero link count are skipped during collection to avoid counting stale `..`.
- Without `ftype`, directory child counts are approximated from backrefs.
- Non-directories and unlinked directories must not have children or backrefs.
- Linked non-root files must have at least one parent.
- Directory tree roots have special parent semantics: `..` is counted as a parent of the root.
- Overflow above `XFS_NLINK_PINNED` is corruption; above `XFS_MAXLINK` is a warning.

Error strategy:
- Collection failures set `INCOMPLETE` aggressively because repair shares the same in-core observations.
- Busy/zapped directories or parent-pointer xattrs abort or mark incomplete instead of producing false corruption reports.
- Sparse array `-EFBIG` is mapped to `-ECANCELED` and incomplete.

This file is tightly coupled to `nlinks.h`, `readdir.c`, `orphanage.c`, `nlinks_repair.c`, `iscan`, `xfarray`, and directory update hooks.
