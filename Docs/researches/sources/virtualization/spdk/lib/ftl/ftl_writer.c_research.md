# File Research: sources/virtualization/spdk/lib/ftl/ftl_writer.c

Implements the sequential base-band writer used by user-data compaction and GC relocation.

Main behavior:
- `ftl_writer_init` initializes queues, limits, halt state, and writer type.
- `get_band` lazily obtains/open-prepares a free band, uses `next_band` when available, enforces a maximum number of open bands split across writers, and sets band ownership callbacks.
- `ftl_writer_run` closes full bands, obtains a writable band, pops one queued `ftl_rq`, and submits it through `ftl_band_rq_write`.
- `ftl_writer_band_state_change` handles `FULL` by moving bands to the full queue and `CLOSED` by releasing ownership and updating last close sequence ID.
- `ftl_writer_is_halted` waits for full bands, active band queue depth, and upgrade padding. During upgrade-prep shutdown it can pad an open band with an internally allocated request.
- `ftl_writer_get_free_blocks` reports remaining user blocks in current and next band.

Role: bridges higher-level relocation/compaction request queues to the low-level band write implementation.
