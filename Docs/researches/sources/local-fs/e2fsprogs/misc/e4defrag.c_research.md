# File Research: sources/local-fs/e2fsprogs/misc/e4defrag.c

## Purpose
Implements `e4defrag`, an online ext4 defragmentation and fragmentation-statistics utility using FIEMAP and `EXT4_IOC_MOVE_EXT`.

## Main Modes
- Default defrag mode:
  - Walks files, creates donor files, preallocates contiguous-ish donor extents, and swaps extents into the target via ioctl.
- Statistic mode `-c`:
  - Computes current extent count, ideal/best extent count, average size per extent, top fragmented files, and score.
- Verbose mode `-v`:
  - Prints per-file progress, extent details, and errors.

## Main Data Structures
- `fiemap_extent_data`: logical, physical, and length in filesystem blocks.
- `fiemap_extent_list`: circular doubly linked list of extents.
- `fiemap_extent_group`: contiguous logical extent group used for donor allocation.
- `move_extent`: ioctl payload for `EXT4_IOC_MOVE_EXT`.
- `frag_statistic_ino`: top-fragmented-file ranking entry.

## Important Functions
- `get_mount_point`: maps a block device to its ext4 mount point using `/etc/mtab` and device numbers.
- `is_ext4`: validates a file/directory is on ext4 and records mount device and `lost+found` path.
- `calc_entry_counts`: counts total and regular files before a tree walk.
- `page_in_core`: uses `mmap` and `mincore` to remember cached pages before moving extents.
- `defrag_fadvise`: syncs and releases pages that were cached by this process.
- `check_free_size`: verifies enough free blocks for donor allocation, accounting for root vs non-root availability.
- `file_frag_count`: asks FIEMAP for mapped extent count.
- `file_check`: validates free space, ownership, and advisory lock status.
- `insert_extent_by_logical` / `insert_extent_by_physical`: sorted insertion with overlap checks.
- `join_extents`: groups logically contiguous extents.
- `get_file_extents`: retrieves FIEMAP extents in batches of 512.
- `change_physical_to_logical`: reorders the extent list from physical to logical order.
- `get_best_count`: estimates ideal extent count based on block groups and flex_bg.
- `file_statistic`: computes per-file fragmentation metrics and top-fragmented rankings.
- `call_defrag`: loops over donor logical extents and invokes `EXT4_IOC_MOVE_EXT`.
- `file_defrag`: validates a file, builds original/donor extent lists, creates/unlinks donor file, fallocates donor regions, compares improvement, and performs defrag.
- `main`: parses args, classifies target type, validates ext4, opens superblock details as root, walks directories/devices, and prints summaries.

## Dependencies
- Linux FIEMAP ioctl.
- ext4 `EXT4_IOC_MOVE_EXT`.
- `nftw64`, mount table parsing, `statfs64`, `fallocate`, `mmap`, `mincore`, `sync_file_range`, `posix_fadvise`.
- ext2fs open for block group/flex_bg metadata used in scoring.

## Notes and Edge Cases
- Skips `lost+found`, non-regular files, empty files, and one-block files.
- Non-root users can only process their own files and get limited statistics.
- Directory walks use `FTW_PHYS | FTW_MOUNT` to avoid symlinks and crossing mount points.
- If donor physical extent count is not better than original, the file is reported OK without moving extents.
- Donor files are created as `file.defrag`, immediately unlinked after open, and used only as temporary extent donors.
- The tool exits nonzero if no target had any successful processing.
