# File Research: sources/os/linux/linux-stable/fs/xfs/scrub/metapath.c

This file scrubs and repairs metadata directory paths. On metadir-enabled filesystems, certain metadata files must be reachable by fixed names under the metadata directory tree; this file verifies and restores those links.

State:
- `struct xchk_metapath` tracks the scrub context, final path component, directory update state, parent directory inode, lock flags, transaction reservations, parent pointer args, and scratch args for removing parent pointers.

Setup:
- `xchk_setup_metapath` accepts metapath selectors in `sm_ino`, rejects non-metadir filesystems and invalid generations, and installs the metadata inode and expected parent/path.
- Runtime feature blocks support realtime metadata paths under `rtgroups` and quota metadata under `quota`.
- Probe mode validates inputs without installing a target.

Scrub:
- `xchk_metapath` allocates an empty transaction, locks parent and child, looks up the expected name in the parent directory, and marks corruption if the dirent is missing or points to the wrong inode.

Repair:
- `xrep_metapath` ensures parent pointer storage if needed, computes link/unlink reservations, then loops:
  - `xrep_metapath_try_link` creates the correct dirent if absent, accepts existing correct links, or reports the wrong child.
  - `xrep_metapath_try_unlink` removes the wrong dirent, including parent pointer cleanup when present, and handles races where the dirent changes.
- `xrep_metapath_link` and `xrep_metapath_unlink` wrap XFS directory child add/remove operations.

Locking:
- `xchk_metapath_ilock_both` locks parent and trylocks child to avoid deadlocks when metadata directories may be corrupt.
- `xchk_metapath_ilock_parent_and_child` does the same for an alleged wrong child during repair.

Important invariants:
- Repair must run after other repairs because it creates transactions and takes ILOCKs.
- Parent directory is required for non-probe scrub/repair.
- Parent pointer updates are conditional on filesystem parent-pointer support.

Risks and edge cases:
- Wrong-child removal handles bogus or unallocated inode numbers by junking the dirent.
- Concurrent changes can return `-EAGAIN` and update the alleged child for retry.
- Missing quota or realtime metadata inodes produce `-ENOENT` at setup.
