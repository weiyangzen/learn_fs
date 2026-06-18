# File Research: sources/os/linux/linux-stable/fs/f2fs/iostat.c

## Purpose

`iostat.c` implements F2FS runtime I/O accounting and latency tracing when `CONFIG_F2FS_IOSTAT` is enabled. It tracks per-superblock byte/count totals, periodic deltas for tracepoints, read folio order statistics, and bio-level latency classified by read/write and page type.

## Main Responsibilities

- Expose a proc-style sequence view through `iostat_info_seq_show()`.
- Maintain cumulative `sbi->iostat_bytes[]` and `sbi->iostat_count[]`.
- Emit periodic `trace_f2fs_iostat()` delta events.
- Track per-bio latency through a mempool-backed `bio_iostat_ctx`.
- Reset and initialize per-filesystem iostat state.
- Initialize and destroy the global bio context slab/mempool.

## Key Functions

- `iostat_info_seq_show()`
  - Returns no output if `sbi->iostat_enable` is false.
  - Prints current time and byte/count/average rows for write, read, and other I/O categories.
  - Includes application data I/O, compressed-data variants, filesystem data/node/meta I/O, GC/checkpoint I/O, discard, flush, zone reset, and read folio order counts.

- `iostat_get_avg_bytes()`
  - Computes average bytes per counted I/O type.
  - Avoids divide-by-zero by returning `0` when count is absent.

- `f2fs_record_iostat()`
  - Periodically snapshots deltas from cumulative counters.
  - Uses `sbi->iostat_next_period` and `sbi->iostat_period_ms`.
  - Double-checks the period under `sbi->iostat_lock`.
  - Updates previous byte/read-folio counters and emits `trace_f2fs_iostat()`.
  - Calls `__record_iostat_latency()` after byte/count tracing.

- `__record_iostat_latency()`
  - Copies `sbi->iostat_io_lat` into a local trace payload under `sbi->iostat_lat_lock`.
  - Converts jiffies to milliseconds for peak and average latency.
  - Resets accumulated latency state after copying.
  - Emits `trace_f2fs_iostat_latency()`.

- `f2fs_reset_iostat()`
  - Clears byte counters, count counters, previous counters, read folio order counters, and latency state.
  - Uses separate locks for byte/count state and latency state.

- `f2fs_update_read_folio_count()`
  - Counts read folio orders, clamping orders above `NR_PAGE_ORDERS - 1`.
  - Triggers periodic iostat tracing afterward.

- `f2fs_update_iostat()`
  - Updates one `enum iostat_type` byte/count pair.
  - Also aggregates buffered/direct app writes into `APP_WRITE_IO`.
  - Also aggregates buffered/direct app reads into `APP_READ_IO`.
  - Under compression, mirrors selected logical data I/O types into compressed-data counters when the inode is compressed.

- `iostat_alloc_and_bind_ctx()`
  - Allocates a `bio_iostat_ctx` from the global mempool.
  - Stores `sbi`, submit timestamp placeholder, page type placeholder, and optional post-read context.
  - Replaces `bio->bi_private` with the iostat context.

- `iostat_update_and_unbind_ctx()`
  - Classifies completed bios as `READ_IO`, `WRITE_SYNC_IO`, or `WRITE_ASYNC_IO`.
  - Restores `bio->bi_private` to the `f2fs_sb_info` for writes and post-read context for reads.
  - Records latency and frees the context.

- `f2fs_init_iostat_processing()` / `f2fs_destroy_iostat_processing()`
  - Manage the global `f2fs_bio_iostat_ctx` slab and mempool.

- `f2fs_init_iostat()` / `f2fs_destroy_iostat()`
  - Initialize per-superblock locks, defaults, disabled state, and latency storage.
  - Free per-superblock latency storage at teardown.

## Important State

- `sbi->iostat_lock`
  - Protects byte/count/read-folio counters and previous snapshots.

- `sbi->iostat_lat_lock`
  - Protects accumulated latency arrays.

- `sbi->iostat_enable`
  - Main runtime gate for accounting.

- `sbi->iostat_period_ms`
  - Periodic trace interval; initialized to `DEFAULT_IOSTAT_PERIOD_MS`.

- `bio_iostat_ctx_pool`
  - Guarantees bio context allocation for iostat instrumentation.

## Interactions

- Called from data, node, segment, checkpoint, GC, file, and compression paths to account I/O.
- `sysfs.c` controls `iostat_enable` and `iostat_period_ms`.
- `data.c` binds/unbinds bio contexts and updates submit timestamps.
- Tracepoints under `trace/events/f2fs.h` consume periodic byte/count and latency snapshots.

## Concurrency and Error Handling

- Counter updates use IRQ-safe spinlocks.
- Periodic tracing is intentionally best-effort and avoids tracing more frequently than configured.
- Latency accounting validates `page_type`; `META_FLUSH` is normalized to `META`, while out-of-range page types warn and are ignored.
- Global allocation setup returns `-ENOMEM` on slab or mempool creation failure.
