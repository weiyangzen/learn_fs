# File Research: sources/os/bsd/freebsd-src/sbin/hastd/hast_compression.c

`hast_compression.c` implements optional payload compression for HAST protocol data.

Key behavior:
- Supports compression names `none`, `hole`, and `lzf`.
- `hole` compression detects all-zero buffers and replaces them with a 32-bit little-endian original size.
- `lzf` compression first tries `hole`; otherwise it attempts LZF when original size is greater than 1024 bytes.
- LZF compressed payloads start with a little-endian original size.
- `compression_send()` may replace the data pointer with a newly allocated compressed buffer and marks `freedatap`.
- `compression_recv()` reverses `hole` or `lzf` compression and updates data pointer/size.
- Unknown compression algorithms or decompression failures are errors.

Important details:
- `allzeros()` probes beginning, middle, and end first, then ORs every 64-bit word.
- It asserts the buffer size is a multiple of 8.
- LZF intentionally allocates less than original size to require useful compression.
