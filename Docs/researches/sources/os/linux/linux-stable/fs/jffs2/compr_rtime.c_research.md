# File Research: sources/os/linux/linux-stable/fs/jffs2/compr_rtime.c

## Role

Implements the JFFS2 rtime compressor, a simple byte-oriented LZ77-like scheme based on last occurrences of each byte value.

## Algorithm

- Maintains `positions[256]`, the last output/source position for each byte value.
- Compression emits pairs:
  - a literal byte;
  - a one-byte repeat length copied from the previous occurrence of that literal’s byte value.
- Runs are capped at 255 bytes.
- Compression fails if output is not smaller than the amount of input consumed.
- Decompression reconstructs output with the same positions table and handles overlapping copies byte-by-byte.

## Key Functions

- `jffs2_rtime_compress()` compresses until source is exhausted or destination space runs out.
- `jffs2_rtime_decompress()` expands literal/repeat pairs and returns an error if a repeat would exceed destination length.
- `jffs2_rtime_init()` registers the compressor.
- `jffs2_rtime_exit()` unregisters it.

## Compressor Registration

`jffs2_rtime_comp` registers:

- priority `JFFS2_RTIME_PRIORITY`;
- name `rtime`;
- compression ID `JFFS2_COMPR_RTIME`;
- compression and decompression callbacks;
- disabled status controlled by `JFFS2_RTIME_DISABLED`.

## Research Notes

This compressor is deliberately simple and byte-aligned. It does not use bit packing or external workspace, making it small and predictable, but generally less powerful than zlib or LZO.
