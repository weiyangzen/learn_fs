# File Research: sources/os/linux/linux/fs/btrfs/zstd.c

## Purpose
Implements the Btrfs zstd compression backend, including level-aware workspace management, compressed-bio creation, compressed-bio decompression, and single-sector decompression.

## Compression Parameters
Btrfs caps zstd window size:
- `ZSTD_BTRFS_MAX_WINDOWLOG = 17`
- `ZSTD_BTRFS_MAX_INPUT = 128 KiB`

Supported levels:
- minimum: `-15`
- maximum: `15`
- default: `3`

`zstd_get_btrfs_parameters()` obtains zstd parameters for a level and input size, then caps `windowLog` to the Btrfs maximum.

## Workspace Model
`struct workspace` contains:
- zstd memory buffer and size
- sector-sized decompression/output scratch buffer
- actual workspace level and requested level
- LRU timestamps/list nodes
- zstd input/output buffers
- cached parameters

Unlike zlib/lzo, zstd uses `struct zstd_workspace_manager`, with:
- one idle list per memory level
- an `active_map` bitmap
- global LRU list
- wait queue
- reclaim timer

## Workspace Management
`zstd_calc_ws_mem_sizes()` precomputes monotonic workspace sizes. This allows a higher-level workspace to safely satisfy lower-level requests even if raw zstd sizes are not naturally monotonic.

`zstd_alloc_workspace_manager()` initializes the manager and tries to preallocate one max-level workspace to guarantee forward progress.

`zstd_get_workspace()`:
- normalizes level 0 to level 1
- first searches idle workspaces at the requested or higher memory level
- allocates a new workspace under NOFS context if none is available
- waits on the max-level workspace if allocation fails

`zstd_put_workspace()` returns a workspace to its level list, updates LRU state only when used at its own level, protects one max-level workspace from reclaim, and wakes waiters when max-level workspace returns.

`zstd_reclaim_timer_fn()` frees idle workspaces unused for `307 * HZ`, skipping workspaces still in use.

## Compression Flow
`zstd_compress_bio()`:
- Initializes a zstd compression stream with Btrfs-capped parameters.
- Maps filemap input folios.
- Allocates compressed output folios.
- Streams input through `zstd_compress_stream()`.
- Adds full output folios to the compressed bio.
- Ends the frame with `zstd_end_stream()`.
- Returns `-E2BIG` if output expansion is detected or output would reach input length.
- Returns `-EIO` for zstd errors and `-ENOMEM` for output-folio allocation failure.

The function tracks `tot_in` and `tot_out`, switches input folios as each is consumed, and unmaps/releases folios on exit.

## Decompression Flow
`zstd_decompress_bio()`:
- Initializes a zstd dstream with `ZSTD_BTRFS_MAX_INPUT`.
- Maps compressed bio folios sequentially.
- Decompresses into the workspace scratch buffer.
- Copies decompressed bytes into target pages through `btrfs_decompress_buf2page()`.
- Advances to the next compressed folio as needed.
- Stops successfully when target pages are filled or the frame ends.
- Returns `-EIO` on zstd error or unexpected input exhaustion.

`zstd_decompress()` handles inline/single-buffer decompression into one destination folio. It expects sector-bounded input/output, copies the decompressed bytes, and zero-fills the destination tail with `-EIO` if output is short.

## Exported Compression Levels
`btrfs_zstd_compress` advertises min/max/default levels for the generic compression layer.

## Concurrency and Memory Notes
- Workspace manager state is protected by a spinlock.
- Timer callback runs in softirq context.
- Workspace allocation is done under `memalloc_nofs_save()` from the get path.
- A max-level workspace is kept available as a forward-progress reserve.

## Risk and Testing Signals
Relevant coverage:
- Negative zstd levels and high positive levels.
- Reuse of higher-level workspaces for lower-level requests.
- Reclaim timer freeing idle workspaces but preserving forward progress.
- Compression expansion fallback.
- Multi-folio input and output.
- Corrupt or truncated compressed streams.
- Short inline decompression with zero-filled destination tail.
