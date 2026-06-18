# File Research: sources/local-fs/e2fsprogs/lib/ext2fs/bitops.h

Defines endian conversion macros, bitmap API declarations, and inline wrappers around generic 32-bit and 64-bit bitmap operations. It is the central public/internal header for libext2fs bitmap bit manipulation.

The endian section maps CPU/LE/BE conversions to no-ops or `ext2fs_swab16/32/64` depending on `WORDS_BIGENDIAN`. The inline section defines fast bit setters/clearers, byte-swap helpers, and typed wrappers for block and inode bitmaps.

The header preserves compatibility with `NO_INLINE_FUNCS` and `INCLUDE_INLINE_FUNCS`: when inlining is disabled it declares external functions, otherwise it emits `_INLINE_` functions. 32-bit bitmap wrappers call `ext2fs_mark_generic_bitmap`, `ext2fs_unmark_generic_bitmap`, and `ext2fs_test_generic_bitmap`; 64-bit wrappers call the generic bmap variants.

Key API groups:
- Raw bit operations: `ext2fs_set_bit`, `ext2fs_clear_bit`, `ext2fs_test_bit`, and 64-bit forms.
- Typed bitmap operations: mark/unmark/test block and inode bitmaps.
- Range operations and first-set/first-zero scans for block and inode bitmaps.
- Generic bitmap/bmap start/end and padding helpers.
- Byte swap helpers and endian conversion macros.

Implementation notes:
- This header is a compatibility bridge between older 32-bit bitmap APIs and newer 64-bit bmap APIs.
- Duplicate declarations for `ext2fs_test_block_bitmap_range2` appear in the extern section.
- Inline “fast” typed bitmap functions still route through generic bitmap functions; “fast” mostly means no old-style warning path or previous-value contract at the typed wrapper layer.
