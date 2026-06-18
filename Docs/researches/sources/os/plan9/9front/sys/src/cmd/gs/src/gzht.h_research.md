# File Research: sources/os/plan9/9front/sys/src/cmd/gs/src/gzht.h

Declares internal halftone construction, sampling, cache, and installation APIs.

Key points:
- Provides allocation and construction functions for spot, threshold, client, and bit-level halftone orders.
- Defines `gs_screen_enum_s` for screen sampling, including supplied halftone, generated order, matrices, strip/shift state, and graphics state.
- Declares screen-order initialization and full screen-plane processing helpers.
- Defines `gx_ht_cache`, which stores cached rendered halftone tiles, cache sizing metadata, copied order, and render callback.
- Defines cache sizing constants for small/large memory modes and tile cache byte limits.
- Provides fractional-color rounding helpers and a small lookup table for low denominators.
- Declares cache allocation/free/init/currentness checks, tile-size checks, tile rendering, order release, device-halftone installation, and transfer-function recomputation.
- Declares colorant-name mapping helpers for halftone dictionaries.

Research notes:
- This is a central internal header for halftone lifecycle and cache performance.
- The cache design deliberately stores only selected rendered levels, sliding cached tiles instead of storing all `P+1` possibilities.
