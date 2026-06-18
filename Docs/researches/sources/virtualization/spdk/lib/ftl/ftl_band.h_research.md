# File Research: sources/virtualization/spdk/lib/ftl/ftl_band.h

## Purpose
Defines FTL band states, metadata format, runtime band structure, and band-level APIs.

## Key Definitions
- `FTL_MAX_OPEN_BANDS` equals `FTL_LAYOUT_REGION_TYPE_P2L_COUNT`.
- Current band metadata version is `FTL_BAND_VERSION_2`.
- `enum ftl_band_state` covers free, prep, opening, open, full, closing, closed.
- `struct ftl_band_md` is packed to exactly one 4096-byte FTL block and stores iterator, state, type, P2L checkpoint region, sequence IDs, write count, durable P2L map object ID, and P2L map CRC.
- `struct ftl_band` stores runtime owner callbacks/refcount, P2L map, relocation flag, band IDs, addresses, metadata request, list entry, and persist callback context.

## API Surface
Declares helpers for address conversion, P2L map acquire/open/release, state/type changes, write prep, GC selection, metadata reads, band open/close/free, request read/write operations, and owner management.

## Dependencies
Includes SPDK bit array, queues, CRC, FTL IO/internal/core, and durable-format helpers.
