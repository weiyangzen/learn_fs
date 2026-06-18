# File Research: sources/os/linux/linux/fs/xfs/scrub/findparent.c

Implements support for finding and validating the parent directory of a directory being repaired. XFS directories have a `..` parent relationship, but repair sometimes must reconstruct or verify it by scanning the directory tree for a non-dot dirent that points to the target inode.

Main components:
- `struct xrep_findparent_info` tracks the directory currently being scanned, the scrub target, optional live parent-scan state, a discovered parent inode, and whether that parent is tentative.
- `xrep_findparent_dirent` is the dirent callback. It ignores non-target entries, rejects invalid names, ignores `.` and `..`, detects multiple parent candidates, records the found parent, and updates parent-scan state.
- `xrep_findparent_walk_directory` locks a candidate directory’s data map, rejects the target itself, temporary repair inodes, mismatched metadata-vs-normal directory trees, sick directories, and zapped directories, then walks dirents.
- `xrep_findparent_live_update` is a directory-update hook used during full scans. If a dirent update affects the scrub target and the parent directory has already been scanned, it updates the scan result.
- `__xrep_findparent_scan_start`, `xrep_findparent_scan`, `xrep_findparent_scan_teardown`, and `xrep_findparent_scan_finish_early` coordinate a live inode scan plus dirent hook so filesystem-wide parent discovery remains valid while directory updates continue.
- `xrep_findparent_confirm` validates a proposed parent by checking root/metadir/unlinked special cases, rejecting bogus or self-referential parent inode numbers, igetting the parent, and confirming it contains a child dirent for the target.
- `xrep_findparent_self_reference` handles directory-tree roots and unlinked directories without scanning.
- `xrep_findparent_from_dcache` queries the VFS dcache for a likely parent as an optimization.

Key invariants:
- Parent discovery cannot hold the target inode ILOCK for the entire filesystem scan, so live dirent hooks are required.
- Metadata directory trees and user directory trees must not be mixed.
- Directories known sick or zapped are not trusted as scan inputs.
- Multiple non-dot parent dirents for one directory are corruption.
