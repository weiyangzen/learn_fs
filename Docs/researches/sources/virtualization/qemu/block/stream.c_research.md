# File Research: sources/virtualization/qemu/block/stream.c

`stream.c` implements QEMU image streaming as a `BlockJob`. Streaming copies data from backing/intermediate images into the active top image, then adjusts the backing chain so the streamed range no longer depends on the old base.

`StreamBlockJob` extends `BlockJob` with a `BlockBackend *blk` for I/O through a temporary copy-on-read filter, pointers for `base_overlay`, `above_base`, `cor_filter_bs`, and `target_bs`, error policy, optional replacement backing string, protocol-masking flag, and whether the original target was read-only. `STREAM_CHUNK` is 512 KiB, the maximum chunk fed to copy-on-read prefetch.

`stream_start()` is the public entry point. It accepts either the older `base` interface or newer `bottom` interface, locates the overlay above the base, reopens the target read-write if necessary, inserts a `copy-on-read` filter above the target with `bottom` set to `base_overlay`, creates a block job on that filter, creates a `BlockBackend` with consistent read/write permissions, disables backend request queuing to avoid drain deadlocks, and blocks graph-changing or write/resize permissions on the active and intermediate nodes. It records all job state and starts the job.

`stream_run()` performs the main copy loop. It obtains the unfiltered target and length under graph lock, exits early if already at `base_overlay`, initializes progress, then scans offsets until the virtual length. For each chunk it yields via `block_job_ratelimit_sleep()`, honors cancellation, checks whether the top image already has data with `bdrv_co_is_allocated()`, and if not, checks whether data exists above the base using `bdrv_co_is_allocated_above()`. When data needs copying, it calls `stream_populate()`, which performs a prefetch read through the copy-on-read filter so the filter writes missing data into the target. Errors are routed through `block_job_error_action()` according to `on_error`, with STOP causing a retryable pause and REPORT ending the loop.

`stream_prepare()` runs at job completion. It drops the copy-on-read filter, drains all block nodes to stabilize the graph, finds the current base relationship, switches the unfiltered target backing child to the selected base with `bdrv_set_backing_hd()`, and updates the on-disk backing file string/format through `bdrv_change_backing_file()`. It handles protocol masking by using `"raw"` when the base is a protocol node and masking was requested.

`stream_clean()` removes any remaining copy-on-read filter, unreferences the job backend, restores read-only state if the job had reopened the image, and frees the backing file string.

Key invariants:
- `base` and `bottom` are mutually exclusive, and `backing_file_str` cannot be used with `bottom`.
- The copy-on-read filter is both the data-copy mechanism and a chain-freezing guard; it is dropped only when the job is ready to change backing.
- Graph locks and drain boundaries are critical because other jobs may mutate the chain while streaming.
- Intermediate nodes are protected because stream assumes each block is read once and remains unchanged.
