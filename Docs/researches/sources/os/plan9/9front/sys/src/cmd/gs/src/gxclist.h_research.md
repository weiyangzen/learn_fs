# File Research: sources/os/plan9/9front/sys/src/cmd/gs/src/gxclist.h

Core command-list type definitions for Ghostscript banded rendering.

Key behavior:
- Documents the two-phase command-list model: record device calls sorted by affected bands, then replay commands band-by-band to render bitmap output.
- Defines `gx_saved_page` and `gx_placed_page` for saving and later compositing banded pages.
- Defines `tile_hash` and `tile_slot` structures for cached halftone/pattern/character bitmaps shared across command-list bands.
- Defines `cmd_prefix` and `cmd_list` for buffered command runs per band plus band-range commands.
- Declares the shared `gx_device_clist_common_members`, including forward target, buffer procedures, bandlist memory, command data buffer, band parameters, page info, tile cache, current band range, and number of bands.
- Defines writer state `gx_device_clist_writer`, including per-band states, command buffer pointers, band-range list, tile-cache tracking, current imager state, dash pattern copy, current clip path, color space, transfer/halftone IDs, image enum state, low-memory/retry fields, and disable flags.
- Defines reader state `gx_device_clist_reader`, including render plane and optional placed-page list for saved-page rendering.
- Defines `gx_device_clist` as a union of common, writer, and reader views.
- Provides `clist_init_params` macro for initializing a clist device before opening.
- Declares clist lifecycle and rendering functions: `clist_finish_page`, `clist_close_output_file`, `clist_close_page_info`, `clist_compute_colors_used`, `clist_setup_params`, and `clist_render_rectangle`.
- Defines disable-mask bits that can force fallback or skip clist support for specific operations.

Dependencies:
- Includes color-space, banding, bits-cache, clist I/O, buffered-device, imager-state, and render-plane headers.
- Expects driver procedures from `gxcldev.h` and related command-list implementation files.

Research notes:
- The invariant for buffered commands requires band-range commands to precede specific-band commands in the buffer; writers must flush when the invariant cannot be preserved.
- Writer fields that point into GC-managed objects are carefully limited; comments warn not to leave dash pattern pointers aimed at the writer’s raw array.
- The reader/writer union means users must know which phase they are in before accessing fields beyond the common prefix.
