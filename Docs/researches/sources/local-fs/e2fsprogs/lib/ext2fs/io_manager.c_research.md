# File Research: sources/local-fs/e2fsprogs/lib/ext2fs/io_manager.c

## Role

Provides generic wrapper helpers for the ext2fs I/O manager abstraction.

## Main Flow

- `io_channel_set_options()` parses `&`-separated `key=value` options and dispatches each to manager `set_option`.
- 64-bit block read/write wrappers prefer manager 64-bit methods and fall back to 32-bit methods if block number fits.
- Optional operations wrap write-byte, discard, zeroout, cache readahead, flock, and unlock.
- `io_channel_alloc_buf()` allocates block-sized/count-sized buffers with optional channel alignment.

## Dependencies

Uses `struct_io_manager` function pointers and `ext2fs_get_memalign()`.

## Risks / Notes

- Optional operations return `EXT2_ET_UNIMPLEMENTED` or `EXT2_ET_OP_NOT_SUPPORTED` depending on wrapper.
- Option parsing mutates a copied string and stops at the first manager error.
