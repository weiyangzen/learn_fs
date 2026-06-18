# File Research: sources/os/linux/linux-stable/fs/jffs2/compr_zlib.c

## Role

Implements the JFFS2 zlib compressor backend using kernel zlib workspaces and stream APIs.

## Key Functions

- `alloc_workspaces()` vmallocs deflate and inflate workspaces.
- `free_workspaces()` releases those workspaces.
- `jffs2_zlib_compress()`:
  - initializes deflate at level 3;
  - reserves `STREAM_END_SPACE` bytes for final stream closure;
  - uses partial flushes while consuming input;
  - finishes with `Z_FINISH`;
  - rejects output that is not smaller than input.
- `jffs2_zlib_decompress()`:
  - initializes inflate;
  - detects normal deflate streams without preset dictionary and skips Adler-32 verification by using negative `wbits`;
  - inflates until stream end and logs non-stream-end returns.
- `jffs2_zlib_init()` allocates workspaces and registers the compressor.
- `jffs2_zlib_exit()` unregisters and frees workspaces.

## Synchronization

- `deflate_mutex` serializes access to the global deflate stream.
- `inflate_mutex` serializes access to the global inflate stream.

## Compressor Registration

`jffs2_zlib_comp` registers:

- priority `JFFS2_ZLIB_PRIORITY`;
- name `zlib`;
- compression ID `JFFS2_COMPR_ZLIB`;
- compression and decompression callbacks;
- disabled state controlled by `JFFS2_ZLIB_DISABLED`.

## Research Notes

zlib is the traditional higher-compression backend. The implementation uses shared global stream objects, so both compression and decompression are serialized separately.
