# File Research: sources/local-fs/btrfs-progs/cmds/filesystem-du.c

## Purpose
Implements `btrfs filesystem du`, a recursive FIEMAP-based disk usage summarizer that reports total, exclusive, and set-shared bytes.

## Data Structures
- `struct shared_extent` is an interval-tree node for physical shared extents.
- `seen_inodes` is an rb-tree of `(inode, subvol)` pairs to avoid double-counting hardlinks.
- `struct du_dir_ctxt` stores aggregate directory totals, directory stream, and a top-level shared-extent tree.

## Accounting Flow
- `du_calc_file_space()` issues repeated `FS_IOC_FIEMAP` calls, skips unknown/delalloc/inline extents, sums total bytes, and records `FIEMAP_EXTENT_SHARED` ranges.
- `du_add_file()` stats and opens a path, resolves the root id for hardlink tracking, recurses into directories, and prints one row unless summary mode suppresses non-top-level rows.
- `du_walk_dir()` iterates regular files and directories under a directory fd and accumulates totals.
- For top-level directories, `count_shared_bytes()` merges overlapping shared physical intervals so shared bytes are counted once per argument set.

## CLI Behavior
Supports `-s/--summarize` and unit options. It warns on very old kernels where `FIEMAP_EXTENT_SHARED` is unavailable. Hardlink detection is reset for each command-line argument.

## Notable Edge Cases
Inline extents are skipped because they do not consume separate data space. Unknown and delalloc extents are skipped because final allocation is not known. Empty subvolume directory inode `2` is treated specially because it has no related tree.
