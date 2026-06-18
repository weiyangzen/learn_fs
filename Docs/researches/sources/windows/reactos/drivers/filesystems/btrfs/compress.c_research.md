# File Research: sources/windows/reactos/drivers/filesystems/btrfs/compress.c

## Purpose

Implements Btrfs compression and decompression support for zlib, LZO, and Zstd, plus the `write_compressed` path that converts file data into compressed Btrfs extents and updates allocation/checksum/extent state.

## Main Components

- Codec setup:
  - zlib included through ReactOS/system or local zlib headers.
  - Zstd included with `ZSTD_STATIC_LINKING_ONLY`.
  - Custom zlib and Zstd allocators backed by kernel pool allocation.
- LZO implementation:
  - `lzo_stream` state.
  - Byte/length/copy/copyback helpers.
  - `do_lzo_decompress`.
  - `lzo_decompress`.
  - LZO 1x-style compressor helpers: `lzo_do_compress`, `lzo1x_1_compress`, `lzo_max_outlen`, `lzo_compress`.
- zlib:
  - `zlib_compress`
  - `zlib_decompress`
- Zstd:
  - `zstd_compress`
  - `zstd_decompress`
- Compressed write path:
  - `comp_part`
  - `write_compressed`

## Codec Behavior

LZO decompression:

- Reads Btrfs LZO page chunks, each prefixed by a 32-bit compressed length.
- Decompresses into 4 KiB pages.
- Zero-fills the remainder of a page if the decompressed output is short.
- Handles Btrfs page-boundary padding before the next page chunk.

zlib compression/decompression:

- Uses zlib stream APIs with kernel-pool custom allocation.
- Compression sets `space_left` to zero when output did not fit, otherwise to remaining output capacity.
- Decompression inflates until stream end or output buffer full.

Zstd compression/decompression:

- Uses advanced stream creation with custom memory callbacks.
- Compression clamps `windowLog` to `ZSTD_BTRFS_MAX_WINDOWLOG` to match Linux Btrfs behavior.
- Reports no space left if input was not fully consumed.

LZO compression:

- Compresses data page-by-page.
- Builds the Btrfs LZO wire format with an overall size header and per-page size headers.
- Copies compressed data to the caller only when it is smaller than the allowed output size.

## `write_compressed` Flow

1. Chooses compression type from mount options, inode property compression, and superblock incompat feature flags.
2. Removes replaced extents with `excise_extents`.
3. Splits the write range into `COMPRESSED_EXTENT_SIZE` parts, normally 128 KiB each.
4. Queues a compression calc job for each part.
5. Helps execute jobs via `calc_thread_main`, waits for completion, and checks job statuses.
6. Marks a part compressed only if at least one filesystem sector is saved; otherwise stores it uncompressed.
7. Sets LZO/Zstd incompat feature flags when those compression formats are actually used.
8. Sector-aligns compressed output and zero-pads the tail.
9. If the first 128 KiB is incompressible and compression was not forced, marks the inode `BTRFS_INODE_NOCOMPRESS`.
10. Concatenates all compressed/uncompressed parts into one write buffer.
11. Finds or allocates a data chunk with enough free space.
12. Reserves logical space with `space_list_subtract`.
13. Writes the data with `write_data_complete`.
14. Calculates checksums unless `BTRFS_INODE_NODATASUM` is set.
15. Adds one `EXTENT_DATA` item per part to the FCB.
16. Copies per-part checksums into extent state.
17. Updates changed extent refs under `changed_extents_lock`.
18. Marks extents and inode dirty.

## Dependencies

- Includes `btrfs_drv.h`.
- Uses `calcthread.c` through `add_calc_job_comp`, `calc_thread_main`, and `do_calc_job`.
- Uses allocation/free-space helpers from write/free-space modules: `find_data_address_in_chunk`, `alloc_chunk`, `space_list_subtract`.
- Uses extent and dirty-state helpers: `add_extent_to_fcb`, `add_changed_extent_ref`, `mark_fcb_dirty`.
- Uses physical/logical write path through `write_data_complete`.

## Research Notes

- This is both codec code and filesystem mutation code; `write_compressed` touches allocation, checksums, extent items, incompat flags, and dirty tracking.
- The compressed-write success criterion is conservative: if compression saves less than one sector, the part is stored uncompressed.
- Zstd feature compatibility is controlled here by setting `BTRFS_INCOMPAT_FLAGS_COMPRESS_ZSTD` once Zstd extents are emitted.
- Notable edge cases to preserve during future work:
  - LZO page framing includes padding logic tied to `LZO_PAGE_SIZE` and `inpageoff`.
  - `write_compressed` assumes rollback-aware free-space and extent updates.
  - Small LZO input handling and LZO input-length calculations are sensitive paths and should be tested if touched.
