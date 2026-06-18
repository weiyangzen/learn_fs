# File Research: sources/os/linux/linux-stable/fs/btrfs/zstd.c

## Purpose

`zstd.c` implements the Btrfs zstd compression backend, including zstd parameter limiting, per-level workspace management, delayed workspace reclaim, bio compression, compressed bio decompression, and single-folio decompression.

## Main Constants

- `ZSTD_BTRFS_MAX_WINDOWLOG` limits the zstd window to 128 KiB.
- `ZSTD_BTRFS_MAX_INPUT` is derived from the max window.
- Supported levels range from `-15` to `15`.
- Default level is `3`.
- Workspace reclaim timeout is `307 * HZ`, intentionally offset from typical transaction timing.

## Workspace Management

- `struct workspace`
  - compression memory buffer and size
  - sectorsize temporary output buffer
  - actual workspace level and requested level
  - last-used timestamp
  - idle/LRU list nodes
  - zstd input/output buffers
  - cached zstd parameters

- `struct zstd_workspace_manager`
  - spinlock
  - global LRU list
  - per-level idle workspace lists
  - bitmap of active levels
  - wait queue
  - reclaim timer

- `zstd_calc_ws_mem_sizes()`
  - Computes monotonic workspace memory requirements so higher-level workspaces can satisfy lower-level requests.
  - Negative fast levels share level-1 sizing.

- `zstd_alloc_workspace_manager()`
  - Initializes manager state and preallocates a max-level workspace when possible.

- `zstd_get_workspace()`
  - Finds an idle workspace at the requested level or higher.
  - Allocates a new workspace under NOFS context.
  - If allocation fails, waits for a max-level workspace to become available.

- `zstd_put_workspace()`
  - Returns a workspace to idle lists.
  - Updates LRU state only for same-level use.
  - Keeps one max-level workspace protected for forward progress.
  - Wakes waiters when max-level workspace returns.

- `zstd_reclaim_timer_fn()`
  - Frees idle workspaces that have aged past the reclaim interval.

## Compression and Decompression

- `zstd_get_btrfs_parameters()` clamps zstd window size to Btrfs’s maximum.
- `zstd_compress_bio()`
  - Initializes a zstd compression stream for the requested level and input length.
  - Maps file folios as input.
  - Writes compressed output into allocated compressed folios.
  - Aborts with `-E2BIG` if compression is not beneficial or output reaches input size.
- `zstd_decompress_bio()`
  - Streams compressed bio folios into the workspace buffer.
  - Copies decompressed ranges into target pages via `btrfs_decompress_buf2page()`.
  - Detects zstd stream errors and short/missing input.
- `zstd_decompress()`
  - Decompresses one small buffer into a destination folio.
  - Zero-fills missing output and returns `-EIO` on short output or stream error.
- `btrfs_zstd_compress`
  - Advertises min, max, and default zstd levels.

## Important Details

- The workspace manager deliberately allows larger workspaces to satisfy smaller-level requests.
- The LRU timestamp is not refreshed when a larger workspace temporarily serves a lower-level request, allowing future reclaim in favor of better-sized workspaces.
- The max-level workspace acts as a forward-progress reserve under memory pressure.
- Compression and decompression maintain local folio mappings and release them on all exit paths.
- Like the zlib backend, this code rejects compressed output that is not smaller than input.

## Dependencies

This file depends on Linux zstd APIs, bitmap/list/timer/waitqueue primitives, folio and bio helpers, Btrfs compression helpers, inode/root metadata, and superblock-to-fs-info accessors.

## Research Notes

`zstd.c` has more internal resource-management logic than `zlib.c` because zstd workspace size varies substantially by compression level. The core behavior is still the standard Btrfs compression backend contract: allocate reusable workspaces, compress filemap input into compressed bios, decompress bios to pages, and fail safely on expansion or malformed streams.
