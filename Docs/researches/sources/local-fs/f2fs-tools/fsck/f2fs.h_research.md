# File Research: sources/local-fs/f2fs-tools/fsck/f2fs.h

## Purpose
Core fsck-side F2FS runtime types, metadata accessors, list helpers, and address/layout macros.

## Key structures
- Lightweight Linux-style list primitives: `struct list_head` plus list add/delete/iterate macros.
- Metadata caches:
  - `struct node_info`
  - `struct f2fs_nm_info`
  - `struct seg_entry`
  - `struct sec_entry`
  - `struct sit_info`
  - `struct curseg_info`
  - `struct f2fs_sm_info`
- Directory/loading state:
  - `struct f2fs_dentry_ptr`
  - `struct dentry`
  - `struct dnode_of_data`
  - `struct hardlink_cache_entry`
- Main fsck mount/runtime state:
  - `struct f2fs_sb_info`

## Key helpers/macros
- Accessors:
  - `F2FS_RAW_SUPER`
  - `F2FS_CKPT`
  - `F2FS_FSCK`
  - `NM_I`
  - `SM_I`
  - `SIT_I`
  - `CURSEG_I`
- Checkpoint/bitmap helpers:
  - `cur_cp_version`
  - `cur_cp_crc`
  - `set_ckpt_flags`
  - `is_set_ckpt_flags`
  - `__bitmap_size`
  - `__bitmap_ptr`
  - `__start_cp_addr`
  - `__start_sum_addr`
- Address mapping:
  - `MAIN_BLKADDR`
  - `SEG0_BLKADDR`
  - `GET_SUM_BLKADDR`
  - `GET_SUM_BLKOFF`
  - `GET_SEGNO`
  - `OFFSET_IN_SEG`
  - `START_BLOCK`
  - `MAX_BLKADDR`
  - `BLKOFF_FROM_MAIN`
- Segment/type helpers:
  - `IS_DATASEG`
  - `IS_NODESEG`
  - `IS_CUR_SEGNO`
- Directory hashing geometry:
  - `dir_buckets`
  - `bucket_blocks`
  - `dir_block_index`
  - `is_dot_dotdot`
- Inline data/xattr helpers:
  - `inline_data_addr`
  - `inline_xattr_addr`
  - `inline_xattr_size`

## External declarations
Declares journal lookup helpers:
- `lookup_nat_in_journal`
- `lookup_sit_in_journal`

## Research notes
This header is the main fsck-local bridge between raw on-disk F2FS definitions from `f2fs_fs.h` and mutable userspace state. Many C files in this directory depend on these macros, so address-calculation changes here have broad blast radius.
