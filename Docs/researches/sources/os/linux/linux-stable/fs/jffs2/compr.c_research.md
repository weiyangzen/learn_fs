# File Research: sources/os/linux/linux-stable/fs/jffs2/compr.c

## Role

Central JFFS2 compression dispatcher. It owns the global compressor registry, selects compression algorithms according to global or mount override policy, handles decompression dispatch, tracks simple compressor statistics, and initializes/exits the built-in compressor modules.

## Key Functions

- `jffs2_compress()` is the main write-path compression API.
  - Honors mount-level compression override when present.
  - Supports modes: none, priority, best size, favour LZO, force LZO, and force zlib.
  - Falls back to `JFFS2_COMPR_NONE` by pointing output at the original input buffer when no compressor produces a smaller result.
- `jffs2_selected_compress()` tries a specific compressor type or the first suitable registered compressor in priority order.
- `jffs2_is_best_compression()` compares compressor results for size-based and LZO-favouring modes.
- `jffs2_decompress()` handles `JFFS2_COMPR_NONE`, `JFFS2_COMPR_ZERO`, and registered decompressor callbacks. It masks legacy bad `usercompr` bits for old zlib-era data.
- `jffs2_register_compressor()` inserts compressors in descending priority order and initializes runtime counters/buffers.
- `jffs2_unregister_compressor()` refuses unregister while the compressor `usecount` is nonzero.
- `jffs2_free_comprbuf()` frees compression output only when it is not the original input buffer.
- `jffs2_compressors_init()` registers zlib, rtime, rubinmips, dynrubin, and lzo, then chooses the default compile-time compression mode.
- `jffs2_compressors_exit()` unregisters the compressors in reverse-ish module order.

## Synchronization and State

- `jffs2_compressor_list_lock` protects the compressor list, per-compressor `usecount`, temporary size-mode buffers, and stats updates.
- Compression callbacks are invoked outside the list spinlock after incrementing `usecount`.
- Size-based modes reuse per-compressor `compr_buf` allocations and detach the winning buffer from the compressor object.

## Research Notes

The file separates policy from compressor implementation. Modern compressors such as zlib and LZO register normally; legacy Rubin compressors can remain present for decompression compatibility. The fallback path is explicit: uncompressed data is represented by returning `JFFS2_COMPR_NONE` and using the caller’s original buffer.
