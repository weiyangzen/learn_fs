# File Research: sources/os/linux/linux/fs/f2fs/iostat.h

Header for F2FS iostat support.

Key definitions:
- `enum iostat_lat_type`: latency buckets for `READ_IO`, `WRITE_SYNC_IO`, and `WRITE_ASYNC_IO`.
- `NUM_PREALLOC_IOSTAT_CTXS`: fixed mempool size for bio context wrappers.
- `DEFAULT_IOSTAT_PERIOD_MS`, `MIN_IOSTAT_PERIOD_MS`, `MAX_IOSTAT_PERIOD_MS`: trace period bounds.
- `struct iostat_lat_info`: sum, peak, and count arrays indexed by latency type and F2FS page type.
- `struct bio_iostat_ctx`: per-bio wrapper storing `sbi`, submit timestamp, page type, and optional post-read context.

Public API when enabled:
- Debug/seq: `iostat_info_seq_show()`.
- Counter control: `f2fs_reset_iostat()`, `f2fs_update_iostat()`, `f2fs_update_read_folio_count()`.
- Bio context control: `iostat_update_submit_ctx()`, `get_post_read_ctx()`, `iostat_update_and_unbind_ctx()`, `iostat_alloc_and_bind_ctx()`.
- Lifecycle: `f2fs_init_iostat_processing()`, `f2fs_destroy_iostat_processing()`, `f2fs_init_iostat()`, `f2fs_destroy_iostat()`.

Disabled configuration behavior:
- Under `#else`, all update/lifecycle functions become no-ops or success stubs.
- `get_post_read_ctx()` returns `bio->bi_private` directly when iostat wrapping is disabled, preserving normal read-post-processing behavior.

Notable contract:
- With iostat enabled, callers must treat `bio->bi_private` as a `bio_iostat_ctx` until `iostat_update_and_unbind_ctx()` restores the original private data.
