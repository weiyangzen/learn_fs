# File Research: sources/os/linux/linux/fs/jffs2/compr.c

This file owns the JFFS2 compressor registry and compression/decompression dispatch. It keeps a global priority-ordered `jffs2_compressor_list` protected by `jffs2_compressor_list_lock`, tracks the active global compression mode, and maintains statistics for uncompressed blocks.

`jffs2_compress()` is the main write-side entry point. It selects either the mount override mode or global default, then handles no compression, priority compression, size-based compression, LZO-favored compression, and forced LZO/ZLIB modes. Priority and forced modes use `jffs2_selected_compress()`, which allocates a temporary output buffer, walks enabled compressors, increments `usecount` while calling the compressor outside the list lock, updates per-compressor stats on success, and returns the selected compression ID. Size and favour-LZO modes try all enabled compressors with each compressor’s reusable `compr_buf`, then choose the smallest or LZO-biased best candidate.

`jffs2_decompress()` normalizes old buggy nonzero `usercompr` upper-byte values, special-cases `JFFS2_COMPR_NONE` and `JFFS2_COMPR_ZERO`, and otherwise locates the matching registered decompressor. Unknown compression types return `-EIO`.

Registration is via `jffs2_register_compressor()` and `jffs2_unregister_compressor()`. Registration initializes scratch-buffer/stat fields and inserts by descending priority. Unregistration refuses active compressors by checking `usecount`.

Initialization registers zlib, rtime, rubinmips, dynrubin, and lzo in order, with rollback on init failure. Default compression mode is selected from `CONFIG_JFFS2_CMODE_*`; otherwise priority mode is used. Exit unregisters compressors in reverse-ish module order.

Key dependencies: `compr.h`, compressor modules, `jffs2_sb_info.mount_opts`, node write/read paths in `write.c`, `read.c`, and GC rewrite paths in `gc.c`.

Important invariants: allocated compressed buffers are freed through `jffs2_free_comprbuf()` only when not equal to the original data pointer; compressors must not be unregistered while `usecount` is nonzero; `JFFS2_COMPR_NONE` means the caller stores the original buffer.
