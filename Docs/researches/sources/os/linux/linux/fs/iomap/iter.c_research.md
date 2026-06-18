# File Research: sources/os/linux/linux/fs/iomap/iter.c

Implements the generic iomap range iterator used by direct I/O, FIEMAP, seek, swapfile activation, and other iomap users.

Key functions:
- `iomap_iter_advance()` advances `iter->pos` and reduces `iter->len`, rejecting advances beyond the current mapping.
- `iomap_iter_clean_fbatch()` releases and reinitializes folio batches when a mapping used `IOMAP_F_FOLIO_BATCH`.
- `iomap_iter_done()` validates mapping invariants, records `iter_start_pos`, and emits destination/source mapping tracepoints.
- `iomap_iter()` drives the two-phase loop:
  - On first entry or after cleanup, calls filesystem `iomap_begin()`.
  - On subsequent entries, computes bytes advanced, calls optional `iomap_end()`, interprets `iter->status`, cleans folio batches, clears previous mappings, and decides whether to continue.

Important semantics:
- Callers loop while return value is positive.
- Leaving `iter.status` unchanged, advancing zero bytes, or exhausting `iter.len` terminates iteration unless a stale mapping is being retried.
- Positive `iter.status` is treated as old invalid semantics and converted to `-EIO`.
- `IOMAP_F_STALE` allows reprocessing when no progress was made.

This file provides the common contract between filesystem mapping providers and iomap consumers.
