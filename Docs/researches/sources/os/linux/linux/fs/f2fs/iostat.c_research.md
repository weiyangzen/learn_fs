# File Research: sources/os/linux/linux/fs/f2fs/iostat.c

Implements F2FS runtime I/O statistics and latency tracing when `CONFIG_F2FS_IOSTAT` is enabled.

Key responsibilities:
- Exposes `iostat_info_seq_show()` for debugfs/seq output of accumulated write, read, discard, flush, zone reset, and read-folio-order counters.
- Maintains byte/count totals in `sbi->iostat_bytes[]`, `sbi->iostat_count[]`, and `sbi->iostat_read_folio_count[]`.
- Periodically emits `trace_f2fs_iostat()` and `trace_f2fs_iostat_latency()` based on `sbi->iostat_period_ms`.
- Tracks per-bio latency through `bio_iostat_ctx`, recording read, sync write, and async write latency by F2FS page type.
- Allocates and destroys global mempool/slab resources for bio iostat contexts.
- Initializes and tears down per-superblock iostat state.

Important functions:
- `iostat_info_seq_show()`: prints current cumulative counters and averages.
- `f2fs_record_iostat()`: computes periodic deltas and emits tracepoints.
- `f2fs_reset_iostat()`: clears byte, count, read-folio, and latency state.
- `f2fs_update_iostat()`: records I/O bytes and derived aggregate/compressed-data counters.
- `f2fs_update_read_folio_count()`: records folio read order distribution.
- `iostat_alloc_and_bind_ctx()` / `iostat_update_and_unbind_ctx()`: wrap `bio->bi_private` with latency context while preserving read post-processing state.
- `f2fs_init_iostat_processing()` / `f2fs_destroy_iostat_processing()`: module-level cache and mempool lifecycle.
- `f2fs_init_iostat()` / `f2fs_destroy_iostat()`: per-mount lifecycle.

Concurrency and locking:
- Counter arrays use `sbi->iostat_lock`.
- Latency arrays use `sbi->iostat_lat_lock`.
- Periodic tracing double-checks `iostat_next_period` under lock to avoid duplicate trace emission.

Notable behavior:
- `APP_WRITE_IO` and `APP_READ_IO` are aggregate counters updated from buffered/direct app I/O.
- Compression builds add parallel compressed-data counters when the inode is compressed.
- `META_FLUSH` latency is folded into `META`.
- Invalid page types during latency accounting warn and skip the sample.

Dependencies:
- Uses F2FS superblock state from `f2fs.h`.
- Uses public declarations and context structs from `iostat.h`.
- Emits F2FS tracepoints from `<trace/events/f2fs.h>`.
