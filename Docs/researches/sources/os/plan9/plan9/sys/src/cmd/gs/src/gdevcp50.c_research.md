# File Research: sources/os/plan9/plan9/sys/src/cmd/gs/src/gdevcp50.c

Ghostscript driver for the Mitsubishi CP50 color printer.

Key responsibilities:
- Defines the `cp50` 24-bit color printer device with empirically derived pixel dimensions, DPI, margins, and clipping constants.
- Implements printer output page handling to pass the requested copy count to the print-page routine.
- Copies rendered scanlines from a fixed source window into R, G, and B plane buffers.
- Rotates each plane into printer order and writes red, green, then blue plane data.
- Emits CP50-specific initialization, mode, copy-count, and image-download command sequences.
- Provides 24-bit RGB color mapping and reverse mapping.

Important behavior:
- Fixed constants define usable image region: `X_PIXEL = 474`, `Y_PIXEL = 800`, `FIRST_LINE = 140`, `LAST_LINE = 933`, `FIRST_COLUMN = 180`.
- Plane buffers are initialized to white before image data is copied.
- `cp50_output_page` opens the printer, stores `num_copies` in a global, calls the print-page proc, closes the printer, then reinitializes clist output if needed.
- The device maps RGB color indices as `R << 16 | G << 8 | B`.

Dependencies:
- Ghostscript printer API from `gdevprn.h`.

Notable risks:
- Uses a global `int copies`, making concurrent device use unsafe.
- `LAST_LINE - FIRST_LINE + 1` is 794, while `Y_PIXEL` is 800; comments say it should be close, not exact.
- Copying uses fixed pixel offsets and assumes the rendered line is large enough for `i * 3 + FIRST_COLUMN + 2`.
- Allocation failure returns `-1` rather than a specific Ghostscript VMerror.
- `cp50_output_page` repeatedly checks `code < 0` after setting `outcode` and `closecode`, so those intermediate errors are only handled later.
