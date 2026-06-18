# sources/user-network-fs/nfs-ganesha/src/FSAL/Stackable_FSALs/FSAL_MDCACHE/mdcache_avl.h

## Purpose

This header defines comparison functions and prototypes for MDCACHE directory-entry AVL indexes. It documents the hash-plus-string ordering model for name lookups and exposes cookie and sorted comparison functions. The source was read as a complete 132-line file.

## Important APIs, Types, and Functions

Inline comparators are `avl_dirent_name_cmpf`, `avl_dirent_ck_cmpf`, and `avl_dirent_sorted_cmpf`. Public prototypes cover the functions implemented in `mdcache_avl.c`: init, insert, cookie insert/lookup, name lookup, deletion, removal, cleanup, and `unchunk_dirent`.

## Control Flow

The name comparator orders first by precomputed `namehash`, then by `strcmp`. The cookie comparator orders by `ck`. The sorted comparator delegates to the sub-FSAL's `dirent_cmp` through the parent sub-handle; it handles the create-time case where one side has not yet been placed into a chunk.

## State and Persistence Behavior

No storage is owned by the header. It defines how existing `mdcache_dir_entry_t` AVL node fields are interpreted while cached directories are alive.

## Dependencies and Integration Points

It includes `mdcache_int.h` and `avltree.h` and is used by readdir, dirent cache, and AVL implementation code. The sorted comparator integrates directly with lower FSAL directory ordering semantics.

## Risks and Edge Cases

Comparator correctness is critical: inconsistent ordering corrupts AVL trees. `avl_dirent_sorted_cmpf` assumes access to a valid parent through at least one chunk and relies on sub-FSAL `dirent_cmp` behavior.

## Test Signals

Unit-style comparator tests for equal hashes with different names, cookie ordering, sorted ordering via a test sub-FSAL, and compile coverage for all callers using the exported prototypes.
