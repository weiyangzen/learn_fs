# File Research: sources/os/plan9/9front/sys/src/cmd/gs/src/gdevprn.h

Common Ghostscript header for memory-buffered printer devices. It defines printer storage policy, device structures, printer-specific procedure vectors, device-construction macros, output-file helpers, buffer-device helpers, scanline access APIs, and compatibility aliases used by many printer backends.

Key contents:
- Defines memory/banding defaults for small and large-memory systems: `PRN_MAX_BITMAP`, `PRN_BUFFER_SPACE`, `PRN_MIN_MEMORY_LEFT`, and related limits.
- Declares abstract printer, async render parameter, page queue, and space-parameter types.
- Defines `gx_printer_device_procs`, including `print_page`, `print_page_copies`, buffer-device callbacks, `get_space_params`, async render thread/open/close hooks, and `buffer_page`.
- Defines `gdev_prn_space_params` with `MaxBitmap`, `BufferSpace`, band parameters, read-only flag, and banding policy (`BandingAuto`, `BandingAlways`, `BandingNever`).
- Defines `gx_prn_device_common`, the common embedded state for printer devices: output filename/stream flags, duplex parameters, page transparency flag, clist/memory buffer fields, async rendering state, clist disable mask, and saved original procs.
- Defines `gx_device_printer` as `gx_device_common` plus printer common state.
- Declares standard printer procedures (`gdev_prn_open`, `gdev_prn_output_page`, `gdev_prn_close`, parameter get/put) and default printer-specific hooks.
- Provides macro families for constructing monochrome, color, extended-color, margins, and copies-capable printer devices.
- Declares output-file APIs (`gdev_prn_open_printer_seekable`, `gdev_prn_open_printer`, `gdev_prn_file_is_new`, `gdev_prn_close_printer`).
- Declares color-use, rectangle rendering, scanline reading, trailing-bit clearing, copy-scanline, memory allocation/reallocation/freeing, buffer-device creation, and compatibility APIs.
- Includes older device-type initialization macros that are explicitly marked unused.

Notable dependencies:
- Core Ghostscript platform, memory, matrix, utility, device, memory-device, clist, render-plane, and parameter headers: `gx.h`, `gp.h`, `gsmatrix.h`, `gsutil.h`, `gxdevice.h`, `gxdevmem.h`, `gxclist.h`, `gxrplane.h`, `gsparam.h`.

Research notes:
- This header is foundational for most printer output devices in this group, including Plan 9 bitmap and PNG devices.
- Many macros initialize large struct fragments; small changes in `gx_prn_device_common` layout or procedure-vector order would affect many device descriptors.
- Async fields are present in the base printer struct even when normal synchronous printers do not use them.
