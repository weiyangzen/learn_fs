# File Research: sources/local-fs/e2fsprogs/lib/ext2fs/get_num_dirs.c

## Role

Estimates the number of directories in a filesystem from group descriptor counters.

## Main Flow

- Validates filesystem magic.
- Sums `ext2fs_bg_used_dirs_count(fs, group)` across all groups.
- If a group reports more directories than `s_inodes_per_group`, adds `max_dirs / 8` as a corruption-tolerant fallback.
- Clamps total to `s_inodes_count`.

## Dependencies

Uses group descriptor accessor helpers from ext2fs internals.

## Risks / Notes

- The file explicitly notes group descriptors can be wrong; result is an estimate used for sizing/sparsity decisions.
