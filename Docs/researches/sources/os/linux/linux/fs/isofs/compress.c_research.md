# File Research: sources/os/linux/linux/fs/isofs/compress.c

Implements transparent zisofs decompression for compressed ISO9660/Rock Ridge files.

Key pieces:
- Uses a global zlib workspace protected by `zisofs_zlib_lock`, avoiding allocation failures during block decompression.
- `zisofs_uncompress_block()` reads compressed filesystem blocks, initializes zlib, inflates one compressed block into one or more page-cache pages, supports sink output for pages not present, marks filled pages uptodate, and handles empty compressed blocks by zeroing pages.
- `zisofs_fill_pages()` locates compressed block pointers from the zisofs header, reads compressed block start/end offsets, validates monotonicity, and calls `zisofs_uncompress_block()` until the requested page is filled.
- `zisofs_read_folio()` determines the compression-block page group, grabs adjacent cache pages opportunistically for readahead-like fill, invokes `zisofs_fill_pages()`, unlocks/releases pages, and returns the critical page error.
- `zisofs_aops` only provides `.read_folio`; bmap is unsupported.
- `zisofs_init()` allocates the zlib workspace; `zisofs_cleanup()` frees it.

The decompressor is read-only and depends on ISOFS block mapping through `isofs_get_blocks()`/`isofs_bread()`.
