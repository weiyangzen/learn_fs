# File Research: sources/local-fs/kdave-linux/fs/btrfs/zstd.c

## Role

`zstd.c` implements Btrfs zstd compression and decompression, including a custom workspace manager optimized for zstd’s level-dependent memory requirements.

## Compression Parameters

Btrfs caps zstd window log at 17, so maximum input window is 128 KiB. Supported levels are `-15` through `15`, with default level `3`. Negative levels are fast zstd modes.

`zstd_get_btrfs_parameters()` obtains zstd parameters and clamps the window log to the Btrfs maximum.

## Workspace Manager

`struct workspace` holds zstd stream memory, size, sector-sized staging buffer, requested level, actual allocated level, LRU metadata, stream buffers, and parameters.

`struct zstd_workspace_manager` maintains:

- spinlock
- global LRU list
- idle lists by clipped level
- bitmap of levels with idle workspaces
- wait queue
- reclaim timer

`zstd_calc_ws_mem_sizes()` precomputes monotonic workspace sizes so a workspace allocated for a higher level can safely serve lower levels.

`zstd_alloc_workspace_manager()` initializes the manager and attempts to preallocate a max-level workspace for forward progress. `zstd_free_workspace_manager()` drains idle workspaces, deletes the timer, and frees the manager.

`zstd_get_workspace()` first searches reusable idle workspaces at or above the requested level. If allocation fails, it waits for a workspace, relying on the protected max-level workspace for progress.

`zstd_put_workspace()` returns a workspace to the idle list, updates LRU state when appropriate, starts the reclaim timer, and wakes waiters when a max-level workspace is returned.

The reclaim timer frees idle workspaces unused for 307 seconds, except in-use workspaces and the protected forward-progress workspace.

## Compression Path

`zstd_compress_bio()` compresses a Btrfs file range into a compressed bio:

- Initializes a zstd compression stream with Btrfs-clamped parameters.
- Maps filemap folios as input.
- Allocates compressed output folios.
- Streams input through `zstd_compress_stream()`.
- Adds full output folios to the bio and finalizes with `zstd_end_stream()`.
- Rejects output that becomes larger than input or reaches the original input length.

Expansion or bio-add failure returns `-E2BIG`; zstd stream errors return `-EIO`.

## Decompression Paths

`zstd_decompress_bio()` initializes a zstd decompression stream, maps compressed bio folios one at a time, streams into the workspace buffer, and copies decompressed chunks to destination pages through `btrfs_decompress_buf2page()`.

`zstd_decompress()` handles direct decompression into one destination folio using the workspace buffer. If decompressed output is shorter than expected, it zero-fills the missing range and returns `-EIO`.

## Error Handling

Compression and decompression log root id, inode number, offset, level, and zstd error codes where available. Input folios are unmapped and released on all exit paths.

## Compression Levels

`btrfs_zstd_compress` publishes the Btrfs zstd level range and default level to the common compression layer.
