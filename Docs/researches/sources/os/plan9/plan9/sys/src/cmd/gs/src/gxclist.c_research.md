# File Research: sources/os/plan9/plan9/sys/src/cmd/gs/src/gxclist.c

## Purpose
Implements command-list device document/page lifecycle code and shared command-list setup for Ghostscript band rendering.

## Main Responsibilities
- Defines GC enumeration/relocation for `gx_device_clist`.
- Defines `gs_clist_device_procs`, the command-list device procedure table.
- Initializes tile cache, band layout, command buffers, and per-band state.
- Opens, closes, rewinds, and finalizes clist band files.
- Ends pages by flushing command buffers and writing terminal band-block entries.
- Computes per-page colors-used metadata.
- Provides VM-error recovery paths for memory-backed band lists.
- Implements `get_band`.

## Key Implementation Details
- A clist device records drawing commands first, then later replays them by band.
- `clist_init_data` partitions one buffer among tile cache, rendering buffer needs, and writer state.
- Band height is either supplied or computed from available buffer space.
- `clist_reset` initializes all per-band `gx_clist_state` records and marks imager/tile parameters unknown.
- `clist_reinit_output_file` sets low-memory warning reserves for command and block files.
- `clist_emit_page_header` writes pass-through target parameters when required by async/partial rendering behavior.
- `clist_end_page` writes `cmd_opv_end_page` and a terminating `cmd_block`.

## Error and Memory Handling
- `permanent_error` blocks future writing after unrecoverable setup/write failures.
- `error_is_retryable` distinguishes recoverable VM warnings from hard VM errors.
- `clist_VMerror_recover` can render/free partial band-list memory without flushing the current page.
- `clist_VMerror_recover_flush` performs a hard flush and resets writer state.

## Dependencies
- `gxclist.h` for core structures.
- `gxcldev.h` and `gxclpath.h` for command-writing helpers and drawing procedure declarations.
- `gxdevmem.h` for buffer device sizing.
- `gsparams.h` for serialized target parameter pass-through.

## Research Notes
This file is the page-level coordinator for banded rendering. The lower-level command encoding and replay logic lives elsewhere, but this file owns allocation geometry, scratch files, page boundaries, and recoverable low-memory behavior.
