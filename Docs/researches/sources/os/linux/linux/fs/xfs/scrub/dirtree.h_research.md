# File Research: sources/os/linux/linux/fs/xfs/scrub/dirtree.h

## Role
Defines shared structures and APIs for directory tree validation and repair.

## Main Types
- `struct xchk_dirpath_step`: one parent-pointer step, containing a stored name cookie, name length, and parent record.
- `enum xchk_dirpath_outcome`: scanner outcomes (`SCANNING`, `DELETE`, `CORRUPT`, `LOOP`, `STALE`, `OK`) plus repair state transitions (`DELETING`, `DELETED`, `ADOPTING`, `ADOPTED`).
- `struct xchk_dirpath`: one path from the scanned directory upward, including first/second step indexes, seen-inode bitmap, step count, path number, and outcome.
- `struct xchk_dirtree_outcomes`: summarized counts of bad/suspect/good paths plus adoption need.
- `struct xchk_dirtree`: full scanner/repair context with root/scan/parent inode numbers, parent pointer scratch state, orphanage adoption state, dirent hook, parent args, lock, hook name buffer, path storage, path list, and stale/aborted bits.

## Interfaces
- Iteration macros for path lists.
- `xchk_dirtree_parentless`: true for roots and zero-link directories.
- `xchk_dirtree_find_paths_to_root`: builds and walks all parent paths.
- `xchk_dirpath_append`: records one path step.
- `xchk_dirtree_evaluate`: summarizes path outcomes.

## Notes
The header is shared by scrub and repair; repair relies on the same recorded path steps to delete bad links or model adoption.
