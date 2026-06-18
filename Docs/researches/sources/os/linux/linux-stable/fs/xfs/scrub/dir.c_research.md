# File Research: sources/os/linux/linux-stable/fs/xfs/scrub/dir.c

## Role

XFS directory scrubber. It validates directory btree records, data/free-space blocks, hash lookup consistency, dirent names and inode numbers, file type fields, parent pointers, and zapped-directory state.

## Key Functions

- `xchk_setup_directory()` prepares directory scrub and repair setup.
- `xchk_directory()` is the top-level directory scrub entry point.
- `xchk_dir_rec()` validates leaf entries against data blocks, real dirents, tags, and name hashes.
- `xchk_directory_blocks()` scans directory data, leaf1, and free blocks for bestfree consistency.
- `xchk_directory_data_bestfree()`, `xchk_directory_leaf1_bestfree()`, and `xchk_directory_free_bestfree()` validate free-space summaries.
- `xchk_dir_actor()` validates each dirent seen by `xchk_dir_walk`.
- `xchk_dir_check_ftype()` compares dirent file type against target inode mode and prevents metadata/regular tree crossing.
- `xchk_dir_check_pptr_fast()` validates child parent pointers when child locks can be acquired.
- `xchk_dir_finish_slow_dirents()` revisits deferred parent pointer checks after lock cycling.
- `xchk_dir_looks_zapped()` detects directories whose data fork was reset by earlier repair.

## Data Structures

- `struct xchk_dirent` stores deferred dirent name cookie, child inode, and name length.
- `struct xchk_dir` holds parent-pointer scratch data and staging arrays/blobs for deferred dirent checks.

## Research Notes

Parent pointer checks are opportunistic first and fall back to a slow path that drops/reacquires locks with revalidation. Clean directories are marked healthy for the zapped-directory sickness bit.
