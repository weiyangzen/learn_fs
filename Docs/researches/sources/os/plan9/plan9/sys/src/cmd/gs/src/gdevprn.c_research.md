# File Research: sources/os/plan9/plan9/sys/src/cmd/gs/src/gdevprn.c

This file is Ghostscript's generic printer driver support layer. It manages printer device opening/closing, output files, memory-vs-banded rendering, command-list setup, buffer devices, scanline extraction, printer parameters, and page output dispatch.

Printer devices are implemented as a union-like structure that can behave either as a memory device or a command-list device. `gdev_prn_open` allocates rendering memory via `gdev_prn_allocate_memory` and optionally opens the output file. `gdev_prn_close` frees memory and closes the current file. `gdev_prn_allocate` is the core allocator: it computes required memory, asks device-specific `get_space_params`/buffer hooks for effective sizing, decides between full-page memory rendering and command-list banding, allocates or resizes backing memory, initializes clist or memory buffer devices, and synthesizes the live device procedure vector by combining render procedures from the selected buffer type with non-rendering procedures from the printer device.

Command-list setup is handled by `gdev_prn_setup_as_command_list`, which allocates command-list buffer space with fallback sizing and opens the clist writer. `gdev_prn_tear_down` reverses either command-list or memory-buffer setup and restores original procedures. Reallocation on parameter changes is handled by `gdev_prn_maybe_realloc_memory`.

Parameter handling exposes `MaxBitmap`, `BufferSpace`, band dimensions, `BandBufferSpace`, `OpenOutputFile`, `ReopenPerPage`, `PageUsesTransparency`, optional `Duplex`, and `OutputFile`. It validates output-file format strings and reads media dictionaries for type checking.

`gdev_prn_output_page` opens the printer file, optionally upgrades `copypage` to `buffer_page`, invokes `print_page_copies`, flushes and checks file errors, closes/reopens per output policy, finishes command-list pages, and calls `gx_finish_output_page`.

The file also supplies public services for printer drivers: rendering plane initialization, colors-used queries for clist bands, buffer-device creation/destruction, memory buffer setup, scanline retrieval (`gdev_prn_get_lines`, `gdev_prn_get_bits`, deprecated `gdev_prn_copy_scan_lines`), trailing-bit clearing, print-scan-line count calculation, output-file open/close helpers, and default async-rendering stubs.

Filesystem relevance: this is the main file-output abstraction for Ghostscript printer devices in this group. It opens/closes named output files through Ghostscript's platform layer, but its core subject is raster printer buffering, not filesystem internals.
