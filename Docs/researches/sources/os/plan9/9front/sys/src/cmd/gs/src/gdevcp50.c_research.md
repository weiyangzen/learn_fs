# File Research: sources/os/plan9/9front/sys/src/cmd/gs/src/gdevcp50.c

Ghostscript Mitsubishi CP50 color printer driver.

Key behavior:
- Defines fixed experimental printer geometry: 474 x 800 pixels, scanline cropping bounds, first column offset, and 154 x 187 DPI.
- `gs_cp50_device` is a 24-bit RGB printer device with custom output page and RGB mappers.
- `cp50_print_page` allocates RGB planes and a temporary plane, initializes them white, emits CP50 control sequences, copies/crops rendered scanlines from `FIRST_LINE` through `LAST_LINE`, splits RGB bytes into separate planes, rotates each plane, and writes R/G/B plane data.
- `cp50_output_page` opens the printer, stores `num_copies` in a global, invokes the print-page routine, closes the printer, reinitializes clist output if needed, and finishes the page.
- `cp50_rgb_color`/`cp50_color_rgb` map 24-bit RGB color indexes.

Notable dependencies:
- Ghostscript printer APIs only.

Research notes:
- Uses a global `int copies` to pass copy count into `cp50_print_page`, so it is not reentrant/thread-safe.
- Allocation failure returns `-1` rather than a Ghostscript VM error code.
- Several geometry constants are empirical and hardcoded, making the driver highly device-specific.
