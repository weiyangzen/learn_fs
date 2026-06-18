# File Research: sources/local-fs/xfsprogs/db/frag.c

Purpose: implements the `frag` command, which estimates filesystem file fragmentation by scanning inode extent maps.

Key behavior:
- Registers `frag [-a] [-d] [-f] [-l] [-q] [-R] [-r] [-v]`.
- If no category flags are supplied, enables all categories: attrs, directories, regular files, symlinks, quota files, realtime metadata files, and realtime files.
- Scans all AGs through AGI inobt roots, reads allocated inode chunks, skips free inodes, and processes selected inodes.
- For each selected data or attr fork, reads extent format or btree format mappings into an `extmap_t`.
- `extmap_ideal` counts how many extents would be needed if logically adjacent extents were merged; this is independent of physical contiguity.
- Accumulates `extcount_actual` and `extcount_ideal`, then reports:
  - Actual extent count.
  - Ideal extent count.
  - Fragmentation factor `(actual - ideal) / actual`.
  - Average extents per file.
- `-v` prints per-inode actual/ideal contribution.

Interactions:
- Uses bmap record conversion, inobt scanning logic, type table cursor reads, sparse inode helpers, and inode fork helpers.
- Shares structural patterns with `check.c` but only computes extent statistics.

Risks/notes:
- The command itself prints that the fragmentation factor is largely meaningless.
- It does not validate btree structure deeply; it scans enough to collect extent records and emits errors for unreadable blocks or invalid bmap record counts.
