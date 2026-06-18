# File Research: sources/os/plan9/plan9/sys/src/cmd/gs/src/gdevprn.h

This header defines the common API, state layout, procedure vectors, and construction macros for Ghostscript memory-buffered printer devices.

It begins by defining memory policy constants for small and large-memory systems: `PRN_MAX_BITMAP`, `PRN_BUFFER_SPACE`, `PRN_MIN_MEMORY_LEFT`, and `PRN_MIN_BUFFER_SPACE`. These determine when a printer renders a full bitmap in memory versus using command-list banding.

`gx_printer_device_procs` is the printer-specific procedure table. It includes `print_page`, `print_page_copies`, buffer-device procedures, `get_space_params`, async render-thread/open/close hooks, and `buffer_page`. This is layered alongside the normal Ghostscript `gx_device_procs`.

`gdev_prn_space_params` stores `MaxBitmap`, `BufferSpace`, `gx_band_params_t`, a read-only flag, and explicit banding mode (`BandingAuto`, `BandingAlways`, `BandingNever`). `gx_prn_device_common` defines the common printer device fields: space parameters, `OutputFile` name, output-file flags, transparency/duplex flags, file state, command-list buffer state, async-rendering state, memory allocators, page queue, clist disable mask, and original device procedures. `gx_device_printer` embeds `gx_device_common` plus these fields.

The header declares standard printer procedures (`gdev_prn_open`, `gdev_prn_output_page`, `gdev_prn_close`, get/put params), default printer-specific callbacks, and procedure-vector construction macros such as `prn_procs`, `prn_color_procs`, and `prn_color_params_procs`.

A large macro section builds printer device descriptors with margins, resolution, color depth, process color fields, and default printer state. These macros are used by nearby devices such as PNG and Plan 9 output.

The utility declarations cover output-file opening/closing, file-new checks, raster size, colors-used queries, rectangle rendering, scanline retrieval, trailing-bit clearing, print-scan-line count, memory allocation/reallocation/free, and buffer-device creation. Compatibility aliases preserve older Ghostscript driver names.

Filesystem relevance: the header defines how printer drivers name and open output files, but otherwise represents raster/printer infrastructure.
