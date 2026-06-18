# File Research: sources/os/linux/linux-stable/fs/jffs2/compr_lzo.c

## Role

Implements the JFFS2 LZO compressor backend using the kernel LZO library.

## Key Functions

- `alloc_workspace()` allocates:
  - `lzo_mem` sized for `LZO1X_MEM_COMPRESS`;
  - `lzo_compress_buf` sized for worst-case compression of one page.
- `free_workspace()` releases both vmalloc-backed buffers.
- `jffs2_lzo_compress()` compresses through `lzo1x_1_compress()`, verifies the compressed output fits the requested destination length, then copies into the caller buffer.
- `jffs2_lzo_decompress()` uses `lzo1x_decompress_safe()` and rejects output length mismatches.
- `jffs2_lzo_init()` allocates workspaces and registers `jffs2_lzo_comp`.
- `jffs2_lzo_exit()` unregisters the compressor and frees workspaces.

## Synchronization

- `deflate_mutex` serializes shared LZO compression workspace use.

## Compressor Registration

`jffs2_lzo_comp` registers:

- priority `JFFS2_LZO_PRIORITY`;
- name `lzo`;
- compression ID `JFFS2_COMPR_LZO`;
- active compression and decompression callbacks;
- `disabled = 0`.

## Research Notes

LZO is designed here as the fast, high-priority compressor. The implementation uses global work buffers rather than per-call allocation, so compression is serialized while decompression has no shared mutable workspace.
