# File Research: sources/local-fs/ocfs2-tools/include/ocfs2/bitops.h

## Purpose

Declares bitmap manipulation helpers for the OCFS2 userspace library.

## Main Contents

- Bit modification/test functions: `ocfs2_set_bit`, `ocfs2_clear_bit`, and `ocfs2_test_bit`.
- Bitmap search helpers for first/next set or clear bit.
- `ocfs2_get_bits_set()` for counting set bits from an offset.

## Dependencies and Integration

- Used by libocfs2 allocation bitmap code and image bitmap logic.
- Notes that implementation is ported from e2fsprogs/ext2fs bitops.

## Research Notes

- Header exposes `int` bit indexes and sizes, so callers must avoid overflowing these parameters for larger logical bitmaps.
