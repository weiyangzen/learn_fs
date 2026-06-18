# File Research: sources/virtualization/spdk/lib/ftl/ftl_debug.c

## Purpose
Provides debug-only band metadata validation and always-available device stats dumping.

## Debug Build Behavior
- `ftl_band_validate_md()` allocates a validation context, walks band P2L entries in chunks of 128 LBAs, pins matching L2P pages, and checks whether valid band P2L entries agree with current L2P mappings unless the current mapping is invalid or in NV cache.
- `ftl_dev_dump_bands()` logs valid-block counts, user-block counts, write counts, and state for all bands.

## Non-Debug Behavior
The header supplies asynchronous no-op validation in non-debug builds to preserve callback timing.

## Stats Dump
`ftl_dev_dump_stats()` logs device UUID, total valid LBAs, total writes, user writes, and write amplification factor; debug builds also log free-band limit counters.

## Dependencies
Uses `spdk/ftl.h`, `ftl_debug.h`, `ftl_band.h`, L2P pinning, bitmap checks, and FTL logging.
