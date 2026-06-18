# File Research: sources/os/linux/linux-stable/fs/iomap/internal.h

Private iomap header for shared implementation helpers.

Contents:
- Defines `IOEND_BATCH_SIZE` as 4096 for completion batching.
- Provides `iomap_max_bio_size()`, which caps bio size to integrity allocation limits when `IOMAP_F_INTEGRITY` is set and otherwise allows `BIO_MAX_SIZE`.
- Declares buffered read and direct ioend completion helpers.
- Declares `iomap_bio_read_folio_range_sync()` when block support is enabled; otherwise provides an `-EIO` warning stub.

This header is used by direct I/O, buffered I/O, and ioend code to keep bio sizing and completion interfaces consistent.
