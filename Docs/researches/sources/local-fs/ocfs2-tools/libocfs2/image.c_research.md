# File Research: sources/local-fs/ocfs2-tools/libocfs2/image.c

Purpose: supports OCFS2 image file bitmap metadata used by o2image-style images.

Key responsibilities:
- Swaps image header fields on big-endian hosts.
- Allocates, frees, loads, marks, tests, and maps image bitmaps.
- Translates filesystem block numbers to compact image block numbers based on set bits.

Important APIs:
- `ocfs2_image_swap_header()`
- `ocfs2_image_free_bitmap()`
- `ocfs2_image_alloc_bitmap()`
- `ocfs2_image_load_bitmap()`
- `ocfs2_image_mark_bitmap()`
- `ocfs2_image_test_bit()`
- `ocfs2_image_get_blockno()`

Core behavior:
- Bitmap block count is derived from filesystem block count and `OCFS2_IMAGE_BITS_IN_BLOCK`.
- Bitmap storage is allocated as an array of bitmap descriptors plus one or more backing allocations.
- Allocation backs off by halving allocation size on `-ENOMEM`, aligned to image bitmap block size.
- Image loading reads and validates header magic, descriptor string, and version.
- Bitmap blocks are read with `pread64()` because image bitmap block size may differ from filesystem block size.
- Each bitmap descriptor stores cumulative set-bit count before the block to support compact block-number mapping.

Dependencies:
- Uses OCFS2 bit operations, image format constants, raw file descriptor from `io_get_fd()`, and low-level block read for the image header.

Notable behavior:
- `ocfs2_image_mark_bitmap()` sets bits but does not update `arr_set_bit_cnt`; that cumulative count is built during load and used for mapping.
- `ocfs2_image_get_blockno()` returns `(uint64_t)-1` when a filesystem block is not present in the image.
- `ocfs2_image_free_bitmap()` assumes `ofs->ost` is valid when called.
