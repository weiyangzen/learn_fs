# File Research: sources/os/plan9/9front/sys/src/cmd/gs/src/zfjpx.c

## Purpose
Creates the `JPXDecode` filter for JPEG 2000 data.

## Key Functions
- `z_jpx_decode()` initializes `stream_jpxd_state`, notes but does not implement the `Colorspace` parameter, and opens the read filter.

## Important Behavior
- Uses `imemory->non_gc_memory` for JPX decoder allocations.
- Passing a dictionary is optional; if present it is checked for read access.
- The `Colorspace` parameter is detected only for diagnostic logging.

## Research Notes
This is a minimal interpreter wrapper around the JPX stream decoder.
