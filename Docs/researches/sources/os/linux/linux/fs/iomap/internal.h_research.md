# File Research: sources/os/linux/linux/fs/iomap/internal.h

Small internal iomap header shared by iomap implementation files.

Contents:
- Defines `IOEND_BATCH_SIZE` as `4096`, used to bound ioend completion batching.
- Defines `iomap_max_bio_size()`, normally `BIO_MAX_SIZE`, but limited by integrity metadata allocation constraints when `IOMAP_F_INTEGRITY` is set.
- Declares buffered read and direct ioend completion helpers:
  - `iomap_finish_ioend_buffered_read()`
  - `iomap_finish_ioend_direct()`
- Provides a `CONFIG_BLOCK`-guarded declaration or stub for `iomap_bio_read_folio_range_sync()`.

The header centralizes internal limits and cross-file prototypes for `direct-io.c`, `ioend.c`, and buffered iomap code outside this group.
