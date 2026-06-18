# File Research: sources/os/linux/linux-stable/fs/xfs/scrub/findparent.h

This header declares the parent-finding scan interface used by XFS online repair.

Key definitions:
- `struct xrep_parent_scan_info` holds the scrub context, live inode scan cursor, directory update hook, mutex-protected `parent_ino`, and a `lookup_parent` flag.
- `xrep_findparent_scan_start` is the default wrapper around `__xrep_findparent_scan_start` with the built-in live update hook.
- `xrep_findparent_scan_found` stores a discovered parent under `pscan->lock`.

Exported operations:
- Start, run, finish early, and tear down a parent scan.
- Confirm a candidate parent inode.
- Detect self-reference cases.
- Query the dcache for a parent hint.

Integration notes:
- Includes `struct xchk_iscan` and `struct xfs_dir_hook`, tying this header directly to live inode scanning and directory-update notifications.
- The mutex exists because scan code and hook callbacks can update `parent_ino` concurrently.
