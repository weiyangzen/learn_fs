# File Research: sources/os/linux/linux/fs/xfs/scrub/findparent.h

Defines the public parent-scan state and entry points used by directory parent repair.

Main declarations:
- `struct xrep_parent_scan_info` stores the scrub context, `xchk_iscan` cursor, dirent hook, mutex-protected discovered parent inode, and a `lookup_parent` flag.
- `__xrep_findparent_scan_start` starts a scan with an optional custom notifier.
- `xrep_findparent_scan_start` wraps the custom start helper with the default live-update hook.
- `xrep_findparent_scan`, `xrep_findparent_scan_teardown`, and `xrep_findparent_scan_finish_early` run and manage scan lifetime.
- `xrep_findparent_scan_found` updates `parent_ino` under mutex.
- `xrep_findparent_confirm`, `xrep_findparent_self_reference`, and `xrep_findparent_from_dcache` expose confirmation and shortcut helpers.

The header couples parent repair to live inode scanning and dirent hook infrastructure while keeping parent result mutation serialized.
