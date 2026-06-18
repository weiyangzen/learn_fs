# File Research: sources/os/plan9/plan9/sys/src/cmd/gs/src/zfjpx.c

## Purpose
Creates the `JPXDecode` filter for JPEG 2000 data.

## Key Functions
- `z_jpx_decode()` initializes `stream_jpxd_state`, notes but does not implement `Colorspace`, and opens the read filter.

## Important Behavior
- Uses `imemory->non_gc_memory` for JPX decoder allocations.
- The `Colorspace` parameter is detected only for diagnostic logging.

## Research Notes
Minimal interpreter wrapper around the JPX stream decoder.
