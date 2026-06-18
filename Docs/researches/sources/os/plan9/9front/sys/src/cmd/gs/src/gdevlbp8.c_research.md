# File Research: sources/os/plan9/9front/sys/src/cmd/gs/src/gdevlbp8.c

Implements Canon `lbp8` and `lips3` monochrome printer devices for Canon LBP-8II and LIPS III printers at 300 dpi.

Key behavior:
- Registers `gs_lbp8_device` and `gs_lips3_device`, each with device-specific paper size, margins, init string, and end string.
- `can_print_page` is the shared print routine.
- It writes printer initialization bytes, scans each Ghostscript raster line, masks unused bits at the right edge, strips trailing zero bytes, and skips empty lines.
- For non-empty rows, it emits vertical motion, horizontal motion, and raster graphics transfer commands.
- Long zero runs inside a row are skipped by splitting the output into shorter non-zero spans.
- Ends the page with an eject command and optional device-specific termination sequence.

Dependencies and notes:
- Uses `gdev_prn_copy_scan_lines` and `gdev_mem_bytes_per_scan_line`.
- The LBP init sequence uses ESC `[` CSI-style sequences; LIPS III uses DCS/ST job control sequences.
- `lbp8_end` is `NULL`, so `sizeof(lbp8_end)` is passed but ignored because the pointer is null.
