# File Research: sources/local-fs/f2fs-tools/fsck/compress.c

## Purpose
Compression support for `sload.f2fs`, plus filename-extension compression filtering.

## Key functionality
- Optional LZO support under `HAVE_LIBLZO2`:
  - Allocates one private buffer containing work memory, raw input buffer, and compressed output buffer.
  - Uses `lzo1x_1_15_compress`.
  - Stores compressed length in little-endian `compress_data.clen`.
- Optional LZ4 support under `HAVE_LIBLZ4`:
  - Allocates one private buffer containing LZ4 state, raw input buffer, and compressed output buffer.
  - Uses `LZ4_compress_fast_extState`.
  - Enforces a max compressed output size based on `c.compress.min_blocks` and `COMPRESS_HEADER_SIZE`.
- `reset_cc()` clears read and compressed buffers for a compression cluster.
- Exposes compression name and ops arrays:
  - `supported_comp_names[] = { "lzo", "lz4", "" }`
  - `supported_comp_ops[]` with NULL operation entries when a library is not compiled in.
- Implements extension filter operations through `ext_filter`:
  - Maintains a linked list of extensions.
  - `add` registers an extension once.
  - `filter` compares path extension against allow/deny mode using `c.compress.filter`.
  - `destroy` frees list nodes.

## Dependencies
- Includes `f2fs.h` and `compress.h`.
- Depends on global config `c.compress`.
- Depends on F2FS constants/types from `f2fs_fs.h`, such as `F2FS_BLKSIZE`, `COMPRESS_HEADER_SIZE`, `compress_ctx`, `compress_data`, `compress_ops`, and `filter_ops`.

## Important behavior
The filter logic uses XOR against `COMPR_FILTER_ALLOW`; this means the same extension list can act as either allow-list or deny-list depending on global compression settings.

## Research notes
The compression buffers are manually laid out inside one allocation. Any changes to cluster size, compression header size, or library work size affect memory layout and must preserve alignment and room for worst-case compressed data.
