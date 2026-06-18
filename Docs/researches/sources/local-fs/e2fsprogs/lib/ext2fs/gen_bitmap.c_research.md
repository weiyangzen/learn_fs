# File Research: sources/local-fs/e2fsprogs/lib/ext2fs/gen_bitmap.c

## Role

Implements legacy 32-bit generic bitmap allocation and operations for inode, block, and generic bitmaps.

## Main Flow

- `ext2fs_make_generic_bitmap()` allocates the bitmap structure, optional description, and rounded backing bytes.
- Mark, unmark, test, clear, resize, copy, compare, range get/set, padding, and first set/zero search functions operate on 32-bit positions.
- If passed a 64-bit bitmap, many old APIs warn via `ext2fs_warn_bitmap32()` and forward to 64-bit implementations.
- Block/inode range helpers test or mutate contiguous ranges.

## Important Details

- `start`, `end`, and `real_end` distinguish valid logical range from allocated backing range.
- Out-of-range tests warn and return false; out-of-range range operations return errors.
- `ext2fs_mem_is_zero()` checks buffers in 256-byte chunks.
- Padding bits past `end` through `real_end` can be marked to prevent accidental allocation.

## Dependencies

Uses low-level bit helpers from ext2fs headers and interoperates with 64-bit bitmap functions from `gen_bitmap64.c`.

## Risks / Notes

- 32-bit APIs cannot represent block numbers above `UINT32_MAX`; forwarding preserves compatibility but callers still need 64-bit-safe entry points.
- `ext2fs_compare_generic_bitmap()` compares whole bytes plus tail bits, so range boundary handling is subtle.
