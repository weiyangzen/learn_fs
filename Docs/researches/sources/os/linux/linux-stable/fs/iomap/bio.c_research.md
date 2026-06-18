# File Research: sources/os/linux/linux-stable/fs/iomap/bio.c

This file implements BIO-backed buffered read helpers for iomap.

Key responsibilities:
- Completes buffered read BIOs by iterating all folios and calling `iomap_finish_folio_read()`.
- Defers failed read completions to workqueue context through `failed_read_work` to avoid nested inode-lock acquisition in filesystem error reporting.
- Allocates and submits read BIOs for contiguous folio ranges in `iomap_read_alloc_bio()` and `iomap_bio_read_folio_range()`.
- Supports caller-provided BIO sets through `iomap_read_folio_ctx->ops->bio_set`, otherwise uses `fs_bio_set`.
- Handles readahead allocation flags and marks BIOs with `REQ_RAHEAD` when appropriate.
- Supports metadata/data integrity payloads when the iomap has `IOMAP_F_INTEGRITY`.
- Provides synchronous single-folio range reads through `iomap_bio_read_folio_range_sync()`.

Important interactions:
- Exports `iomap_bio_read_folio_range`, `iomap_bio_read_ops`, and sync read helper for use by buffered iomap code and filesystems.
- Depends on `iomap_sector()`, `iomap_max_bio_size()`, and the current `iomap_iter` mapping.
- Integrates with folio completion logic in `buffered-io.c`.

Notable invariants and risks:
- BIO coalescing requires contiguous sectors and enough remaining max BIO size.
- Failed reads are queued after dropping the spinlock; ownership of the BIO transfers to the failure work item.
- Allocation fallback retries a single-page BIO after larger BIO allocation failure to avoid partial-page read complexity.

Research notes:
- This file is the block-device read submission backend for iomap buffered reads; higher-level folio state tracking lives in `buffered-io.c`.
