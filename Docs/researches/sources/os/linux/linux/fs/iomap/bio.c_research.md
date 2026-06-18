# File Research: sources/os/linux/linux/fs/iomap/bio.c

BIO-backed buffered read helper implementation for iomap.

Main behavior:
- Ends read BIOs by iterating all folio segments and calling `iomap_finish_folio_read()`.
- Defers failed buffered read completion to `failed_read_work` to avoid nested `i_lock` acquisition in filesystem error-reporting paths.
- Allocates and chains read BIOs in `iomap_bio_read_folio_range()`, merging contiguous sectors when possible and splitting when the bio is absent, non-contiguous, too large, or cannot accept another folio.
- Uses a caller-provided `bio_set` when available, otherwise `fs_bio_set`.
- Adds integrity payloads when `IOMAP_F_INTEGRITY` is set.
- Provides synchronous single-range read helper `iomap_bio_read_folio_range_sync()` with integrity verification.

Exports:
- `iomap_bio_read_folio_range`
- `iomap_bio_read_ops`
- `iomap_bio_read_folio_range_sync`

Risks:
- Failed BIO ownership transfers into the global failed-read list after locking; callers must not reuse the BIO.
- Readahead uses `__GFP_NORETRY | __GFP_NOWARN` and falls back to a single-page bio to avoid partial-page read complexity.
- Integrity allocation/free and verification must match the source iomap flags.
