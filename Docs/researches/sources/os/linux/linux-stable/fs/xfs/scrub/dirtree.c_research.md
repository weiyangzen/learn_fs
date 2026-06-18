# File Research: sources/os/linux/linux-stable/fs/xfs/scrub/dirtree.c

## Role

Validates XFS directory tree structure using parent pointers. It walks each parent-pointer path from the target directory upward to the relevant root and detects cycles, multiple parents, missing parents, stale paths, and disconnected structures.

## Key Functions

- `xchk_setup_dirtree()` prepares dirtree scrub, enables directory hooks, creates path storage, and sets up inode contents.
- `xchk_dirtree()` is the top-level dirtree scrub entry point.
- `xchk_dirtree_create_path()` creates a tracked path for each parent pointer on the target directory.
- `xchk_dirpath_append()` records one parent-link step and marks seen inodes.
- `xchk_dirpath_walk_upwards()` walks one path toward the root while temporarily dropping the target ILOCK.
- `xchk_dirpath_step_up()` validates each parent pointer step, detects roots, direct/distant cycles, bad generations, nondirectory parents, unlinked parents, tree crossing, and zapped parent pointers.
- `xchk_dirtree_live_update()` marks collected paths stale when concurrent directory updates touch them.
- `xchk_dirtree_find_paths_to_root()` repeats path collection and walking until no stale update invalidates results.
- `xchk_dirtree_evaluate()` summarizes path outcomes into good, bad, suspect, and adoption-needed categories.
- `xchk_dirtree_parentless()` identifies root or unlinked directories that should not have parents.

## Research Notes

The algorithm is incremental instead of freezing the filesystem. It relies on parent pointers, ILOCK synchronization, and live directory update hooks to restart when concurrent modifications invalidate scanned path state.
