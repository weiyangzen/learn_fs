# File Research: sources/local-fs/f2fs-tools/mkfs/f2fs_format.c

Implements the actual `mkfs.f2fs` formatting algorithm: compute layout, initialize metadata areas, create initial filesystem objects, write checkpoint packs, and write superblocks.

Key responsibilities:
- Maintains global raw superblock `raw_sb`, `sb`, and checkpoint pointer `cp`.
- Device helpers choose target device ranges, handle aliased devices, compute next/last zones, and avoid placing active segments on alias-only regions.
- Defines default cold/hot extension lists and merges user extension lists into the superblock.
- `f2fs_prepare_super_block()` is the layout core:
  - Sets magic/version/block geometry.
  - Computes segment0 alignment, device segment ranges, multi-device metadata/device boundaries, zoned alignment constraints, total segment counts, SIT/NAT/SSA sizes, checkpoint payload size, main-area start, section/main segment counts, overprovision/reserved segments, UUID, root/node/meta ino values, quota/lost+found/alias ino reservations, active segment placement, version strings, casefold settings, feature bits, and optional superblock checksum.
- `f2fs_init_sit_area()` and `f2fs_init_nat_area()` zero initial SIT and NAT sets.
- `f2fs_write_check_point_pack()` constructs the first valid checkpoint pack:
  - Initializes checkpoint counters, current segment numbers/offsets, valid node/data counts, free/user blocks, checkpoint flags, bitmap sizes, checksum.
  - Writes compact data summary with NAT/SIT journals, node summaries, second checkpoint page, optional NAT bits, and an invalid second checkpoint pack with version zero.
- `f2fs_write_super_block()` writes two superblock copies with the superblock at byte offset 1024 inside each block.
- Root construction:
  - `add_dentry()` serializes directory entries into dentry blocks.
  - `f2fs_add_default_dentry_root()` creates `.`, `..`, optional `lost+found`, and optional alias-file dentries.
  - `f2fs_write_root_inode()` initializes and writes the root inode plus root dentry data block.
- Quota construction:
  - `f2fs_write_default_quota()` synthesizes v2 quota file contents.
  - `f2fs_write_qf_inode()` creates quota inodes and points them at quota data blocks.
- Optional `lost+found` construction creates its dentry block and inode.
- Device alias support:
  - Creates pinned regular-file inodes representing aliased devices.
  - Marks corresponding SIT entries fully valid as cold data and sets inode extent to the aliased device range.
- `f2fs_create_root_dir()` orchestrates root, quota, lost+found, alias, obsolete dnode cleanup, and default NAT updates.
- `f2fs_format_device()` is the high-level formatter sequence: prepare superblock, trim, initialize SIT/NAT, create root objects, write checkpoint, write superblock.

Important dependencies:
- Uses `f2fs_fs.h` for on-disk ABI and helpers.
- Uses `quota.h` for quota file layout.
- Uses `f2fs_format_utils.h` for discard/trim.
- Uses lower-level device I/O helpers declared in `f2fs_fs.h`.

Behavioral notes:
- The formatter is very layout-sensitive; many values are rounded to segment/zone boundaries.
- Zoned mode has strict checks: metadata must fit in conventional/random zones, and trim is required by main.
- Readonly F2FS feature images use a reduced active-log model and no overprovision/reserved segments.
- Metadata journals are initialized in summary-block spare areas rather than immediately writing all NAT/SIT entries.
