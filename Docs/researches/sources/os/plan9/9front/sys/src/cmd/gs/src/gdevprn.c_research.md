# File Research: sources/os/plan9/9front/sys/src/cmd/gs/src/gdevprn.c

Generic Ghostscript printer-device support. It decides whether pages render into full memory buffers or command-list bands, manages printer parameters and output files, synthesizes procedure vectors, and exposes scanline retrieval helpers used by concrete printer drivers.

Key behavior:
- Defines GC hooks for printer devices, treating the underlying storage as either a clist device or forwarding/memory device depending on `buffer_space`.
- Exports `prn_std_procs`, the standard open/output/close procedure set for printer devices.
- `gdev_prn_open` initializes printer memory and optionally opens `OutputFile`; `gdev_prn_close` frees memory and closes an open output stream.
- `gdev_prn_allocate` is the core allocator. It computes buffer requirements from buffer-device callbacks, accounts for PDF 1.4 transparency scratch space, asks driver-specific `get_space_params` for overrides, chooses full bitmap or command-list banding, allocates or resizes storage, opens clist devices when needed, and splices printer procedures with memory/clist rendering procedures.
- `gdev_prn_setup_as_command_list` allocates command-list buffer memory, initializes clist parameters, and retries with larger buffers on some limit errors.
- `gdev_prn_tear_down`, `gdev_prn_free_memory`, and reallocation helpers restore original procedures and detach/free the current backing store.
- Default async-rendering hooks return unknown errors unless `gdevprna.c` overrides them.
- `gdev_prn_get_params` and `gdev_prn_put_params` expose printer controls: `MaxBitmap`, `BufferSpace`, band sizing, `OpenOutputFile`, `ReopenPerPage`, `PageUsesTransparency`, optional `Duplex`, and `OutputFile`.
- `validate_output_file` checks Ghostscript output filename syntax and percent-format usage.
- `gdev_prn_output_page` opens output, optionally upgrades `copypage` to `buffer_page`, calls the concrete `print_page_copies`, flushes and checks file errors, closes per-page files, finalizes clists, and calls `gx_finish_output_page`.
- `gx_default_print_page_copies` implements multi-copy output by repeatedly printing, closing/reopening per page, and correcting `PageCount`.
- `gx_render_plane_init`, `gdev_prn_colors_used`, and `gx_page_info_colors_used` support plane rendering and band color-use analysis.
- `gx_default_create_buf_device` creates memory buffer devices and optionally wraps them in a plane extraction device for selected-plane rendering.
- `gx_default_size_buf_device`, `gx_default_setup_buf_device`, and `gx_default_destroy_buf_device` size, initialize, and free memory/plane-extraction buffer devices.
- `gdev_prn_get_lines`, `gdev_prn_get_bits`, and `gdev_prn_copy_scan_lines` retrieve rendered scanlines from full memory or clist-backed devices, with trailing-bit cleanup.
- `gdev_prn_close_printer` closes output when the filename pattern or `ReopenPerPage` requires per-page reopening.
- `gdev_prn_maybe_realloc_memory` reallocates printer backing storage when size, space parameters, or transparency usage changes on an open device.

Notable dependencies:
- Printer declarations from `gdevprn.h`.
- Ghostscript filename, device, parameter, clist I/O, get-bits, plane extraction, and transparency support: `gsfname.h`, `gsdevice.h`, `gxclio.h`, `gxgetbit.h`, `gdevplnx.h`, `gstrans.h`.

Research notes:
- This file is a central integration layer for many printer backends in the Ghostscript tree.
- The printer object overlays memory-device and clist-device storage via the `skip` area defined in `gdevprn.h`; procedure-vector restoration is therefore a key invariant.
- Some comments mark behavior as questionable or hacky, especially buffer-device setup and print-device procedure synthesis.
- If `gdev_prn_put_params` changes `OutputFile` while a file is open, it closes the old stream before copying the new name.
