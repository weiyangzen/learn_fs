# File Research: sources/os/linux/linux-stable/fs/xfs/scrub/dirtree_repair.c

## Role

Repairs directory tree structural problems found by the parent-pointer dirtree scrubber. It deletes unwanted incoming directory links and adopts parentless directories into the orphanage.

## Key Functions

- `xrep_setup_dirtree()` ensures the orphanage can exist before repair.
- `xrep_dirtree()` is the top-level repair entry point and reruns scans when results become stale.
- `xrep_dirtree_decide_fate()` chooses which paths to keep, delete, or adopt.
- `xrep_dirtree_delete_all_paths()`, `xrep_dirtree_keep_one_good_path()`, and `xrep_dirtree_keep_one_suspect_path()` rewrite path outcomes according to repair policy.
- `xrep_dirpath_retain_parent()` records the surviving parent for dotdot repair.
- `xrep_dirtree_delete_path()` loads the target path, drops scan resources, deletes the bad incoming link, and restores scrub state.
- `xrep_dirtree_unlink()` removes the parent dirent, adjusts link counts, updates dotdot if needed, removes parent pointer xattrs, notifies hooks, purges dcache, and commits.
- `xrep_dirtree_adopt()` and `xrep_dirtree_move_to_orphanage()` reparent an orphaned directory into lost+found/orphanage.
- `xrep_dirtree_create_adoption_path()` creates a synthetic path so live update hooks can observe in-progress adoption.
- `xrep_dirtree_fix_problems()` executes planned deletions and adoption.

## Repair Strategy

Parentless roots or unlinked directories should have no parent paths. Normal directories should have exactly one surviving path to root. Extra good/suspect paths are deleted; zero surviving paths trigger orphanage adoption if possible.

## Research Notes

The repair logic is tightly coupled to live update invalidation. Any concurrent change that makes path evidence stale causes repair to rescan before proceeding.
