# File Research: sources/local-fs/e2fsprogs/e2fsck/dx_dirinfo.c

## Purpose
Maintains metadata for indexed/HTREE directories that require validation, repair, or rehashing.

## Data Model
Uses `ctx->dx_dir_info`, a sorted array of `struct dx_dir_info`. Each entry records:
- directory inode,
- hash version,
- casefold hash marker,
- number of directory blocks,
- per-block `dx_dirblock_info` array.

## Main Behavior
- `e2fsck_add_dx_dir()` allocates/grows the array and inserts sorted by inode.
- Tracks whether directory hashing is casefold-aware via `EXT4_CASEFOLD_FL`.
- `e2fsck_get_dx_dir_info()` uses binary search.
- `e2fsck_free_dx_dir_info()` frees each per-directory block array and the main table.
- Count and iterator helpers expose the table to pass/rehash code.

## Integration
Used by pass 1/2 and directory rehash logic for indexed directories. Public declarations are in `e2fsck.h`.

## Risks / Notes
Sorted insertion is required for lookup correctness, similar to `dirinfo.c`.
