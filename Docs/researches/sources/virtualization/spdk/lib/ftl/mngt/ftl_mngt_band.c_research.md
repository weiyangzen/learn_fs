# File Research: sources/virtualization/spdk/lib/ftl/mngt/ftl_mngt_band.c

Management helpers for band allocation, metadata binding, physical grouping, address initialization, and startup finalization.

Important flows:
- `ftl_dev_init_bands` calculates usable band count from base bdev size minus reserved base metadata bands, allocates band array, and initially places bands on `shut_bands`.
- `ftl_band_init_md` attaches per-band metadata and valid-map slices.
- `decorate_bands` groups logical bands into larger physical reclaim units, dropping unaligned tail bands.
- `ftl_mngt_initialize_band_address` sets each band start and tail metadata address from the base data region.
- `ftl_recover_max_seq` combines max band and NV-cache sequence IDs into `sb->seq_id` and writer/NV-cache last sequence IDs.
- `ftl_mngt_finalize_init_bands` classifies free/shut/open bands, reattaches open bands to user/GC writers, restores P2L maps from SHM or checkpoints, recalculates free counts/limits, and validates GC can start.

This file is central to recovering writer state after startup and ensuring GC has a viable path when free bands are scarce.
