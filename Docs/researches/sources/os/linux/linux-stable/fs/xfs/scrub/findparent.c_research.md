# File Research: sources/os/linux/linux-stable/fs/xfs/scrub/findparent.c

This file implements the online repair helper for finding the parent directory of a directory inode. It supports brute-force filesystem directory scans, live directory-update hooks, special-case self references, and a dcache shortcut.

Key structures and state:
- `struct xrep_findparent_info` tracks the directory currently being scanned, the scrub context, optional scan state, the discovered parent inode, and whether that parent was only tentatively observed.
- It depends on the live inode scanner from `iscan.c`, directory walkers, dirent hooks, tempfile filtering, and XFS inode health flags.

Main control flow:
- `__xrep_findparent_scan_start` validates that dirent fsgates are enabled, initializes `xchk_iscan`, registers a directory hook, and initializes `parent_ino` under a mutex.
- `xrep_findparent_scan` iterates every allocated inode with `xchk_iscan_iter`, filters to directories, scans each directory for a child entry pointing at `sc->ip`, marks visited inodes, and releases references.
- `xrep_findparent_dirent` ignores invalid, dot, and dotdot names, records a single valid parent, rejects multiple parents as corruption, and updates `xrep_parent_scan_info` if present.
- `xrep_findparent_live_update` applies dirent add/remove notifications for directories already visited by the live scan, keeping the scan result coherent with concurrent changes.
- `xrep_findparent_confirm` verifies a proposed parent by special-casing root/metadir root/unlinked directories, validating the parent inode number, loading it, checking it is a directory, and scanning it.
- `xrep_findparent_self_reference` returns known self-parent values for root directories and root fallback for unlinked directories.
- `xrep_findparent_from_dcache` tries `d_find_alias` and `dget_parent` as a fast parent hint.

Important invariants:
- The target directory’s ILOCK is not held during full filesystem scans; callers must retake it before reading results.
- Scanned directories are skipped if they are the target, a repair tempfile, in the wrong metadata tree, sick in core/bmbtd/dir, or zapped.
- Multiple parent dirents for one directory are treated as corruption.
- Live updates are selected only for already visited inode ranges via `xchk_iscan_want_live_update`.

Risks and edge cases:
- Corrupt directory entries, sick directories, or zapped directories abort or defer repair rather than producing unreliable parent results.
- Dcache lookup is only a hint and is not a consistency proof.
- The scan relies on dirent fsgates and hooks to avoid missing concurrent parent changes.
