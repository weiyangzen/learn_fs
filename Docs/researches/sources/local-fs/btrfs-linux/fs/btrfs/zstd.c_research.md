# File Research: sources/local-fs/btrfs-linux/fs/btrfs/zstd.c

This file implements the Btrfs zstd compression backend: zstd parameter limiting, per-level workspace management, idle workspace reclaim, compression into `compressed_bio`, bio decompression, inline/single-buffer decompression, and advertised zstd compression levels.

Zstd limits:
- `ZSTD_BTRFS_MAX_WINDOWLOG` is 17, capping the window to 128 KiB.
- `ZSTD_BTRFS_MAX_INPUT` is derived from that window limit.
- Supported levels range from `-15` through `15`, with default level `3`.
- `zstd_get_btrfs_parameters()` gets kernel zstd parameters for a level and source length, then caps `windowLog` to Btrfs’s maximum.

Workspace model:
- `struct workspace` stores zstd memory, memory size, sector-sized output buffer, allocated level, requested level, last-used timestamp, list nodes, zstd input/output buffers, and current parameters.
- `struct zstd_workspace_manager` owns a lock, global LRU, idle workspace lists by clipped level, active-level bitmap, wait queue, and reclaim timer.
- `clip_level()` maps the public compression level to an internal zero-based index; negative fast-mode levels use level-1 workspace sizing.
- `zstd_calc_ws_mem_sizes()` precomputes monotonic workspace memory requirements across all supported levels so a higher-level workspace can satisfy lower-level requests.

Workspace lifecycle:
- `zstd_alloc_workspace_manager()` allocates the manager, initializes lists/waitqueue/timer, stores it in `fs_info->compr_wsm[BTRFS_COMPRESS_ZSTD]`, calculates memory sizes, and tries to preallocate one max-level workspace for forward progress.
- `zstd_free_workspace_manager()` removes the manager from `fs_info`, frees idle workspaces from all level lists, deletes the reclaim timer, and frees the manager.
- `zstd_alloc_workspace()` allocates one workspace, its zstd memory, and its sector-sized buffer.
- `zstd_free_workspace()` frees a workspace.
- `zstd_find_workspace()` searches idle workspace lists at or above the requested level, removes a matching workspace, and marks its requested level.
- `zstd_get_workspace()` finds or allocates a workspace. If allocation fails under memory pressure, it sleeps on the manager wait queue and retries, relying on the protected max-level workspace for forward progress.
- `zstd_put_workspace()` returns a workspace to its idle list, updates LRU state for matching requested/allocated levels, hides one max-level workspace from reclaim, arms the reclaim timer, clears `req_level`, and wakes waiters when a max-level workspace returns.
- `zstd_reclaim_timer_fn()` scans the LRU and frees idle workspaces unused for `ZSTD_BTRFS_RECLAIM_JIFFIES`.

Compression path:
- `zstd_compress_bio()` initializes a zstd compression stream with Btrfs-capped parameters and the requested level.
- It maps filemap folios as input, allocates compressed output folios, streams input through `zstd_compress_stream()`, and adds full or final output folios to the compressed bio.
- It rejects compression when output grows beyond input or cannot fit into the target bio, returning `-E2BIG`.
- It returns `-EIO` for zstd stream errors and `-ENOMEM` for output folio allocation failure.
- It unmaps input folios and frees unused output folios on exit.

Bio decompression:
- `zstd_decompress_bio()` initializes a zstd dstream with `ZSTD_BTRFS_MAX_INPUT`, maps compressed bio folios, inflates into the workspace buffer, and copies decompressed bytes into the target pages with `btrfs_decompress_buf2page()`.
- It advances through compressed input folios as each input buffer is consumed.
- It detects zstd errors and invalid input exhaustion as `-EIO`.

Inline/single-buffer decompression:
- `zstd_decompress()` initializes a dstream, points input at the provided memory buffer, inflates into the workspace sector-sized buffer, copies the produced bytes into the destination folio, and zero-fills any missing tail.
- Short output is treated as `-EIO`.

Compression levels:
- `btrfs_zstd_compress` advertises min `-15`, max `15`, and default `3`.

Cross-file relationships:
- Registered through Btrfs compression infrastructure in `compression.h`.
- Uses `compressed_bio`, compressed folio allocation/free, and `btrfs_decompress_buf2page()`.
- Stores its workspace manager in `fs_info->compr_wsm[BTRFS_COMPRESS_ZSTD]`.
- Uses `btrfs_sb()` from `super.h` in single-buffer decompression to retrieve `fs_info`.

Important invariants and risks:
- Workspace sizes are intentionally monotonic so higher-level workspaces can be reused for lower-level requests.
- At least one max-level workspace is protected from reclaim to preserve forward progress during allocation failure.
- `req_level` distinguishes the caller-requested level from the allocated workspace level; LRU updates only happen when they correspond.
- The zstd window is capped to keep compressed extents within Btrfs’s decompression assumptions.
- Compression must produce fewer bytes than input; otherwise the backend reports `-E2BIG`.
- All mapped input folios must be unmapped and put on all paths.
- Decompression short output zero-fills the destination tail and reports error.
