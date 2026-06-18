# File Research: sources/os/linux/linux-stable/fs/isofs/compress.c

Implements transparent zisofs decompression for compressed files on ISO 9660.

Key paths:
- `zisofs_read_folio()` determines the compression block covering the requested page, opportunistically grabs adjacent pages for readahead, and calls `zisofs_fill_pages()`.
- `zisofs_fill_pages()` reads the compressed block pointer table, validates block boundaries, and invokes decompression for each compression block.
- `zisofs_uncompress_block()` reads compressed disk blocks, serializes zlib use with `zisofs_zlib_lock`, inflates into target pages or a sink page, marks completed pages uptodate, and reports critical-page errors.
- `zisofs_init()` allocates a global zlib workspace with `vmalloc()`, and `zisofs_cleanup()` frees it.

Important details:
- Empty compressed blocks zero-fill target pages.
- Compressed block size is bounded by `deflateBound()`.
- The global workspace avoids allocation failures during decompression but requires a mutex because zlib workspace use is not concurrent.
- `zisofs_aops` only supplies `.read_folio`; bmap is intentionally unsupported.
