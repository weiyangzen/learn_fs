# File Research: sources/os/linux/linux/fs/xfs/scrub/dirtree.c

## Role
Validates the tree structure of parent-pointer-enabled XFS directories by walking each parent pointer path upward from a target directory to the relevant root. It detects multiple parents, cycles, disconnected paths, stale scan data, and corrupt parent pointer chains.

## Setup and State
- `xchk_setup_dirtree` enables directory hooks, optionally sets up repair, allocates `struct xchk_dirtree`, creates xfarray/xfblob storage for path steps and names, and sets up inode-content scrub locking.
- `xchk_dirtree_buf_cleanup` removes hooks and frees all path state.

## Path Construction
- `xchk_dirtree_create_path` creates one `struct xchk_dirpath` per parent pointer on the target directory.
- `xchk_dirpath_append` records path steps in sequential xfarray entries, stores names in xfblob, and tracks seen inode numbers in a bitmap to detect loops.

## Upward Walk
- `xchk_dirpath_revalidate` confirms the target directory's first parent pointer still exists after locks may have been cycled.
- `xchk_dirpath_step_up` igets and locks each parent directory, validates generation, directory type, link count, metadir tree consistency, zapped parent-pointer state, and scans for exactly one parent pointer to continue upward.
- Outcomes include OK at root, DELETE for a path that returns to the scanned inode, LOOP for ancestor cycles, CORRUPT for bad or ambiguous parents, and STALE for invalidated scans.

## Live Update Handling
- `xchk_dirtree_live_update` receives directory update notifications.
- Each update is compared against recorded path steps by parent inode, child inode, and dirent name.
- Matching external updates mark the scan stale; updates caused by repair advance deleting/adopting state.
- Stale scans are discarded and retried.

## Evaluation
- `xchk_dirtree_find_paths_to_root` repeatedly creates paths and walks them until no stale invalidation occurs.
- `xchk_dirtree_evaluate` counts bad, suspect, and good paths.
- `xchk_dirtree` marks corruption if parentless directories have paths, normal directories have zero or multiple acceptable paths, direct bad paths exist, or suspect paths require xref corruption.

## Invariants
- Requires parent-pointer feature support.
- The root inode is chosen according to regular root versus metadata directory root.
- The scanner drops the target ILOCK while walking ancestors but keeps enough state plus live hooks to detect races.
