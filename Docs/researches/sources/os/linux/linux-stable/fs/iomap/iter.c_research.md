# File Research: sources/os/linux/linux-stable/fs/iomap/iter.c

Implements the generic iomap range iterator.

Key paths:
- `iomap_iter_advance()` advances `iter->pos` and reduces `iter->len`, warning if the caller advances beyond the current mapping.
- `iomap_iter()` alternates between ending the previous mapping with optional `ops->iomap_end()` and beginning the next mapping with `ops->iomap_begin()`.
- `iomap_iter_reset_iomap()` releases any folio batch attached via `IOMAP_F_FOLIO_BATCH` and clears `iomap` and `srcmap`.
- `iomap_iter_done()` validates mapping bounds, rejects stale mappings, records `iter_start_pos`, and emits tracepoints for destination and source mappings.

Loop contract:
- Callers continue while `iomap_iter()` returns positive.
- To stop from inside the loop, callers leave `iter.status` unchanged or set it negative.
- Positive `iter.status` is treated as old semantics and converted to `-EIO`.
- If a mapping is marked stale, the iterator can retry without forward progress.
