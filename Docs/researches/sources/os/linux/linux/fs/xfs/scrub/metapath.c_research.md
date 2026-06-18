# File Research: sources/os/linux/linux/fs/xfs/scrub/metapath.c

Scrubs and repairs metadata-directory paths. On metadir filesystems, key metadata files are reachable through paths under the metadata directory tree; this scrubber verifies that the expected directory entry points to the expected incore metadata inode.

Setup:
- `struct xchk_metapath` tracks scrub context, expected name, parent directory, child inode, locks, reservations, parent-pointer state, and scratch lookup args.
- `xchk_setup_metapath_scan` installs the target metadata inode, allocates state, stores parent/path, and builds an `xfs_name`.
- RT helpers set up `/rtgroups` and rtgroup metadata inode paths when realtime is enabled.
- Quota helpers set up `/quota` and per-quota inode paths when quota support is enabled.
- `xchk_setup_metapath` validates metadir support, rejects generation-based requests, handles probe, and dispatches by `sm_ino` metapath selector.

Scrub:
- `xchk_metapath_ilock_both` locks parent and child safely, retrying child lock with termination checks.
- `xchk_metapath` handles probe, requires a parent, allocates an empty transaction, locks both inodes, looks up the expected dirent in the parent, and marks corruption if missing or pointing to the wrong inode.

Repair, under online repair:
- `xrep_metapath_link` creates the expected dirent and parent pointer if enabled.
- `xrep_metapath_unlink` removes an incorrect dirent and optional parent pointer from the alleged child.
- `xrep_metapath_try_link` attempts to create the correct link, reporting the wrong child if a conflicting dirent exists.
- `xrep_metapath_try_unlink` removes the wrong child link, handling bogus/missing child inodes and races where the dirent changed.
- `xrep_metapath` ensures the child has an attr fork for parent pointers, computes link/unlink reservations, and loops link/unlink attempts until the path is correct or an error occurs.

Important invariants:
- Repairs run after other repairs because they create transactions and take ILOCKs.
- The parent directory itself might be corrupt, so locking is cautious.
- Parent pointers are maintained when the filesystem supports them.
