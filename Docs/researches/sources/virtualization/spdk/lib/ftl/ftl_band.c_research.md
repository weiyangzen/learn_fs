# File Research: sources/virtualization/spdk/lib/ftl/ftl_band.c

## Purpose
Implements FTL band metadata, address math, P2L map allocation/lifetime, state transitions, valid-block accounting, and garbage-collection candidate selection.

## Main Behavior
- Computes tail metadata placement and detects when a band's user area is full.
- Transitions bands among free, prep, opening, open, full, closing, and closed states.
- Allocates P2L map buffers from durable-format-aware mempools and frees them only when refcounts reach zero.
- Acquires P2L checkpoint regions for active writes and records checkpoint region type in band metadata.
- Converts between physical `ftl_addr`, band ID, and band-relative block offset.
- Tracks valid entries through `p2l_map.num_valid` and global `valid_map`.
- Calculates band invalidity as `1 - valid/user_blocks`.

## GC Selection
- Closed, non-relocating bands are eligible.
- Physical-band groups are scored by average invalidity, then write count, then physical ID.
- Supports a high-priority GC band ID from shared superblock state.
- Persists/resets GC iterator state depending on create mode, clean shutdown, fast startup, or fast recovery.

## Startup Helpers
- `ftl_valid_map_load_state()` reconstructs each band's valid count from its valid bitmap.
- `ftl_bands_load_state()` validates band metadata versions and restores free bands to the runtime free list.

## Dependencies
Uses FTL core/layout/debug/internal APIs, CRC utilities, FTL mempools, bitmap helpers, and P2L checkpoint APIs.
