# File Research: sources/local-fs/xfsprogs/repair/pptr.c

## Role

`pptr.c` validates and repairs XFS directory parent pointer xattrs. It builds a filesystem-wide expected parent-pointer index from phase 6 directory entries, then compares that index against actual `ATTR_PARENT` extended attributes on every live inode.

## Data Model

- `nameblobs` stores deduplicated directory entry names globally.
- `fs_pptrs[agno].pptr_recs` stores expected parent pointer records per child AG.
- `ag_pptr` records expected `(child_agino, parent_ino, parent_gen, namehash, name_cookie)`.
- `file_pptr` records actual xattr parent pointers found on a single inode.
- Garbage parent-pointer xattrs are staged in slabs plus xfblob name/value storage for later removal.

## Core Flow

- `parent_ptr_init()` allocates per-AG slabs and global string storage if the filesystem has parent pointers.
- `add_parent_ptr()` is called by phase 6 for each surviving directory entry to record the expected child-parent-name tuple.
- `check_parent_ptrs()` processes AGs in parallel.
- `check_ag_parent_ptrs()` sorts expected records and scans every live inode in the AG.
- `check_file_parent_ptrs()` walks xattrs, records valid parent pointers, stages malformed parent xattrs, removes garbage, and calls `crosscheck_file_parent_ptrs()`.
- `crosscheck_file_parent_ptrs()` lockstep-compares expected and actual records, adding missing pptrs, removing extra pptrs, and replacing mismatched generation/name records.
- `try_erase_parent_ptrs()` removes all parent pointer xattrs from metadata files before they are relinked into metadata directories.

## Dependencies

This file uses libxfs parent pointer helpers, xattr walking, slabs, xfblob/strblobs temporary storage, workqueues, repair inode trees, and global no-modify behavior.

## Risk Areas

- Correctness depends on phase 6 only recording entries that survive directory repair.
- Name cookies are used as comparison keys, so global name storage consistency is critical.
- Duplicate records can arise from `..` reprocessing; `AG_PPTR_POSSIBLE_DUP` suppresses exact duplicate additions.
- The implementation repairs parent pointers from directory entries, not directories from parent pointer data.
