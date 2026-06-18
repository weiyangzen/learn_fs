# File Research: sources/os/plan9/9front/sys/src/cmd/gs/src/gxclist.c

Implements Ghostscript command-list document/page lifecycle and shared clist device setup. It prepares banded rendering state, opens band-list files, finalizes pages, and handles low-memory recovery.

Key behavior:
- Defines the GC descriptor for `gx_device_clist`, tracing forwarding-device pointers plus writer-only image clip/color-space and imager-state references.
- Exports `gs_clist_device_procs`, a device procedure table that records drawing operations into command lists and later supports band rendering.
- Defines `clist_imager_state_initial` used to initialize writer-side cached graphics state.
- Partitions the shared buffer into tile/bitmap cache, band rendering space, per-band states, and command buffer.
- `clist_tile_cache_size` and `clist_init_tile_cache` size and initialize a bitmap/tile cache with a hash table and bits-cache chunk.
- `clist_init_bands` validates band buffer size, sets band height, and computes number of bands.
- `clist_init_states` allocates per-band `gx_clist_state` records and command-buffer bounds inside the remaining data buffer.
- `clist_init_data`, `clist_reset`, and `clist_init` fully initialize or reset writer state, including tile parameters, known-state flags, imager state, transfer IDs, halftone ID, and image enum ID.
- Opens command and block band files through `clist_open_output_file`, supporting externally managed files when requested.
- `clist_reinit_output_file` sets memory-warning reserves sized for pending block and command writes when partial-page recovery is available.
- `clist_emit_page_header` writes current device parameters into the clist when pass-through parameter recording is required.
- `clist_end_page` flushes the command buffer, writes a terminating block entry, computes colors-used summaries, records block-file end position, and releases low-memory reserve margins.
- Provides `clist_VMerror_recover` and `clist_VMerror_recover_flush` for retrying recoverable low-memory cases by rendering partial bandlist contents and resetting state.
- `clist_finish_page` rewinds or appends band files after page output and reinitializes the clist writer for the next page.
- `clist_get_band` returns the band span containing a given Y coordinate.

Dependencies:
- Uses `gxcldev.h`, `gxclpath.h`, `gxdevmem.h`, banding structures from `gxband.h`, file abstraction from `gxclio.h`, and Ghostscript parameter/color/device helpers.
- Calls drawing-command writers implemented in other clist files, including path/image/color/rectangle routines.

Research notes:
- The device uses `ymin < 0` to distinguish writer state from reader state for GC scanning.
- Buffer partitioning is idempotent so it can also be used as a sizing check.
- The low-memory path distinguishes retryable VM errors from permanent errors and relies on target printer partial-page rendering support.
