# File Research: sources/local-fs/btrfs-linux/fs/btrfs/zlib.c

This file implements the Btrfs zlib compression backend: workspace allocation, workspace cleanup, whole-compressed-extent bio compression, bio decompression, inline/single-sector decompression, and supported compression-level metadata.

Workspace model:
- `struct workspace` wraps a kernel `z_stream`, allocated zlib workspace memory, a staging buffer, buffer size, list node, and current compression level.
- `zlib_get_workspace()` obtains a generic Btrfs compression workspace for the requested level and stores that level in the zlib workspace.
- `zlib_alloc_workspace()` allocates the wrapper, zlib deflate/inflate workspace memory, and a staging buffer.
- `zlib_free_workspace()` frees the zlib workspace, staging buffer, and wrapper.
- On s390 with zlib hardware acceleration, `need_special_buffer()` requests a 4-page staging buffer unless Btrfs minimum folio size is already large enough.

Compression path:
- `zlib_compress_bio()` initializes deflate with the selected level, streams filemap folio contents through zlib, allocates compressed output folios, adds output folios to `compressed_bio`, and rejects compression that grows the data.
- It uses `btrfs_compress_filemap_get_folio()` and `btrfs_calc_input_length()` for filemap input.
- Normal input mode maps file folios directly with `kmap_local_folio()`.
- s390 hardware mode uses `copy_data_into_buffer()` to copy enough file data into the larger workspace buffer before calling zlib.
- It aborts with `-E2BIG` when output exceeds input length or early output is already larger than useful.
- It returns `-ENOMEM` on compressed folio allocation failure and `-EIO` on zlib initialization or stream errors.

Bio decompression:
- `zlib_decompress_bio()` maps compressed bio folios one at a time, initializes inflate, optionally skips the zlib header/adler32 check for raw deflate when safe, inflates into the workspace buffer, and copies decompressed bytes into target pages through `btrfs_decompress_buf2page()`.
- It advances compressed input with `bio_next_folio()` and validates expected folio sizing against `btrfs_min_folio_size()`.
- It logs and returns `-EIO` if the stream does not end cleanly.

Inline/single-buffer decompression:
- `zlib_decompress()` inflates from a provided memory buffer into one destination folio at `dest_pgoff`.
- It expects input and output to fit within one sector-sized workspace buffer.
- It zero-fills any trailing destination range if decompression produced fewer bytes than expected and returns `-EIO`.

Compression levels:
- `btrfs_zlib_compress` advertises min level `1`, max level `9`, and Btrfs default zlib level.

Cross-file relationships:
- Registered through the compression backend table declared in `compression.h`.
- Uses `compressed_bio`, compressed folio allocation/freeing, and decompression copy helpers from Btrfs compression code.
- Uses `fs_info->sectorsize` and `btrfs_min_folio_size()` for staging and output sizing.
- Uses inode/root identifiers only for diagnostics.

Important invariants and risks:
- Output folios added to the bio must exactly account for `workspace->strm.total_out`.
- The backend deliberately rejects compressed output that is not smaller than input.
- All `kmap_local_folio()` mappings must be released before return, including error paths.
- The s390 hardware path depends on the staging buffer being large enough for hardware-efficient deflate.
- `zlib_deflateEnd()` and `zlib_inflateEnd()` must be called after successful stream initialization.
- Short decompression is treated as corruption and zero-fills the missing destination bytes.
