# File Research: sources/os/linux/linux-stable/fs/xfs/scrub/dirtree.h

## Role

Shared state and interfaces for directory tree scrub and repair.

## Key Definitions

- `struct xchk_dirpath_step` stores one path step: dirent name cookie/length and parent record.
- `enum xchk_dirpath_outcome` records scan outcomes and repair-in-progress states.
- `struct xchk_dirpath` tracks one parent-pointer path, seen inode bitmap, step indexes, path number, and outcome.
- `struct xchk_dirtree_outcomes` summarizes path evaluation counts and adoption need.
- `struct xchk_dirtree` is the main scan/repair context, including root/scan/parent inodes, scratch parent-pointer args, orphanage adoption state, live update hook, mutex, path arrays/blobs, and stale/aborted flags.

## API Surface

- Path/scanner helpers: `xchk_dirtree_find_paths_to_root`, `xchk_dirpath_append`, `xchk_dirtree_evaluate`, `xchk_dirtree_parentless`.
- Iteration macros for safe and normal path-list traversal.

## Research Notes

The header is intentionally shared by `dirtree.c` and `dirtree_repair.c`, allowing repair to reuse the exact path evidence gathered during scrub.
