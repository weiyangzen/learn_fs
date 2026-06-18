# File Research: sources/os/linux/linux-stable/fs/xfs/scrub/parent_repair.c

This file repairs parent relationship metadata.

For filesystems without parent pointers:
- Repair finds a credible parent for a directory and resets `..` if needed.
- It avoids unhealthy directories because directory repair can rebuild directory contents directly.

For filesystems with parent pointers:
- Repair reconstructs the target inode’s parent-pointer xattrs by scanning every directory in the filesystem for dirents pointing to the target.
- It builds a new attr fork in a temporary file, copies non-parent xattrs, replays parent-pointer additions/removals, and atomically exchanges attr fork mappings.

Key structures:
- `struct xrep_parent`: repair state, including parent-pointer staging arrays/blobs, xattr staging arrays/blobs, temporary exchange state, findparent/iscan state, orphanage adoption state, buffers, and counters.
- `struct xrep_pptr`: stashed parent-pointer update, including name cookie, parent record, name length, and add/remove action.
- `struct xrep_parent_xattr`: stashed non-parent xattr key/value metadata.

Setup:
- `xrep_setup_parent` enables dirent gates, allocates repair state, creates a temporary file, and tries to attach/create orphanage.
- `xrep_parent_setup_scan` either starts legacy findparent scanning or initializes parent-pointer rebuild scratch storage and live update hooks.
- Parent-pointer repair requires rmapbt and exchange-range support.

Directory scan and live updates:
- `xrep_parent_scan_dirtree` drops target ILOCK and scans all inodes with an empty transaction.
- `xrep_parent_scan_file` walks directories and calls `xrep_parent_scan_dirent`.
- Relevant dirents are converted into parent-pointer additions staged in `pptr_recs`/`pptr_names`.
- `xrep_parent_live_update` captures concurrent dirent changes for already-scanned directories and stages add/remove actions.
- Staged parent-pointer updates are periodically flushed to the temporary file to cap memory use.

Xattr copying:
- `xrep_parent_copy_xattrs` copies all non-parent, complete xattrs from the target to the temporary file.
- Remote values are fetched with `xrep_parent_fetch_xattr_remote`.
- Stashed xattrs are flushed periodically by `xrep_parent_flush_xattrs`.
- If a parent-pointer update happens while ILOCK is dropped for flushing, the copy restarts without opportunistic flushing.

Commit:
- `xrep_parent_finalize_tempfile` replays all remaining parent-pointer updates, ensures both target and temp have attr forks, and allocates the exchange transaction.
- `xrep_parent_rebuild_pptrs` copies xattrs, locks the temp file, finalizes staged pointers, swaps attr forks with `xrep_xattr_swap`, resets the temp fork, and records a found parent if possible.
- `xrep_parent_rebuild_tree` optionally moves parentless files into `/lost+found` or resets directory `..`.

Post-rebuild:
- `xrep_parent_set_nondir_nlink` counts parent pointers on non-directories, fixes unlinked-list membership, and sets `i_nlink`.

This is one of the most complex files in the group because it combines full-filesystem scanning, live dirent hooks, temporary inode exchange, xattr preservation, parent-pointer reconstruction, orphanage adoption, and link-count cleanup.
