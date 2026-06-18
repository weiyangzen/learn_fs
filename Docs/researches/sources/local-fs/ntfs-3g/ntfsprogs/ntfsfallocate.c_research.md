# File Research: sources/local-fs/ntfs-3g/ntfsprogs/ntfsfallocate.c

## Role

Implements `ntfsfallocate`, a direct NTFS attribute preallocation tool that fills holes in a requested byte range, optionally extending apparent file size.

## Main Functions

- `parse_options()` parses length/offset with suffixes, device, file, attribute type, attribute name, and mode flags.
- `ntfs_save_rl()` copies the original runlist for rollback.
- `ntfs_restore_rl()` frees newly allocated clusters that overlap holes in the original runlist and restores mapping pairs after errors.
- `ntfs_inner_zero()` zeroes newly allocated clusters that are before initialized size.
- `ntfs_merge_allocation()` merges newly allocated runs into the attribute runlist, updates sparse/compressed-size accounting, and writes mapping pairs.
- `ntfs_inner_allocation()` finds holes overlapping the requested VCN range and allocates clusters with `ntfs_cluster_alloc()`.
- `ntfs_full_allocation()` handles extension versus hole-filling, restores initialized size, computes apparent size according to `--no-size-change`, and updates the attribute record and inode size fields.
- `ntfs_fallocate()` opens/maps the target attribute, rejects compressed files, saves sizes/runlist, performs allocation, rolls back on error, and marks filename/inode dirty.
- `main()` checks mount state, mounts with read-only/no-action or recovery/force flags, resolves the path, runs allocation, closes inode, unmounts, and frees attribute name storage.

## Dependencies

Uses libntfs-3g attribute, inode, layout, volume, runlist, directory/pathname, bitmap, cluster allocation (`lcnalloc.h`), utilities, and logging.

## Important Behavior

Compressed attributes are rejected. Sparse attributes are accounted by increasing `compressed_size`; once compressed size reaches allocated size the sparse flag is cleared. Allocated clusters that become visible before initialized size are zeroed to avoid exposing stale disk data.

On allocation failure, the code attempts to restore original inode sizes, free newly allocated clusters, restore the saved runlist, and preserve `errno`.

## Research Notes

This utility mutates low-level allocation state directly. The option parser has a suspicious extra `optind++` after accepting an attribute name, which can consume an additional argument before the final arity check.
