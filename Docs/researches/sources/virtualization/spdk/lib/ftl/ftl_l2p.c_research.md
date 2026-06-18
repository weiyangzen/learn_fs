# File Research: sources/virtualization/spdk/lib/ftl/ftl_l2p.c

## Purpose
Dispatches L2P operations to either the flat or cached backend and implements shared L2P update semantics.

## Backend Selection
Uses compile-time macro `SPDK_FTL_L2P_FLAT`:
- Defined: routes `FTL_L2P_OP(name)` to `ftl_l2p_flat_name`.
- Default: routes to `ftl_l2p_cache_name`.

## Common API
Initializes deferred pin list, wraps pin/unpin/set/get/clear/restore/persist/trim/process/halt/resume, and completes/defer pins through `ftl_l2p_pin_complete()`.

## Update Semantics
- `ftl_l2p_update_cache()` handles user writes to NV cache. It resolves write-after-write races by chunk sequence ID or address ordering within the same chunk, ignores writes older than trim metadata, updates NV-cache P2L/valid state before L2P, then invalidates old address.
- `ftl_l2p_update_base()` handles GC/compaction writes to base. It updates base band valid state and L2P only if current L2P still matches the expected old address; otherwise it invalidates the new relocated address. Old address is invalidated afterward.

## Dependencies
Uses FTL band, NV cache, cached L2P, flat L2P, trim metadata, and core-thread assertions.
