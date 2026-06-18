# File Research: sources/os/bsd/freebsd-src/sys/fs/p9fs/p9_protocol.c

This file implements 9P protocol buffer serialization and deserialization.

Core abstraction:
- `struct p9_buffer` is treated as a typed byte stream with size, capacity, offset, tag, id, and data pointer.
- `buf_read()` copies from current offset and advances it.
- `buf_write()` appends to current size and advances size.

Format mini-language:
- `b`: 8-bit integer.
- `w`: 16-bit integer.
- `d`: 32-bit integer.
- `q`: 64-bit integer.
- `s`: counted string.
- `u`: uid.
- `g`: gid.
- `Q`: 9P qid.
- `S`: legacy/9P2000.u stat structure.
- `A`: 9P2000.L getattr/stat structure.
- `D`: data blob with 32-bit length.
- `T`: string array.
- `R`: qid array.
- `W`: string with explicit length, write-only.
- `?`: stop processing if protocol is not `.u` or `.L`.

Key functions:
- `p9_buf_readf()` and internal `p9_buf_vreadf()` decode typed fields.
- `p9_buf_vwritef()` and internal `p9_buf_writef()` encode typed fields.
- `p9stat_read()` decodes a stat blob into `p9_wstat`.
- `p9_buf_prepare()` writes an initial placeholder 9P header.
- `p9_buf_finalize()` rewrites the true size at the beginning of the buffer.
- `p9_buf_reset()` clears size and offset.
- `p9_dirent_read()` parses one directory entry from a returned readdir buffer.

Memory behavior:
- Decoding strings allocates `M_TEMP` NUL-terminated strings.
- Decoding string/qid arrays allocates arrays and cleans them on failure.
- `stat_free()` frees dynamically allocated fields in `p9_wstat`.

Research-relevant risks:
- Wire integer encoding is copied directly via host memory representation; portability depends on the broader kernel/transport assumptions.
- `p9_buf_vwritef()` caps normal string length at 255.
- `p9_dirent_read()` uses `strncpy()` for the parsed name but does not explicitly NUL-terminate beyond the copied length; consumers rely on `len`.
- `D` decode returns a pointer into the response buffer; callers must copy before freeing the request.
