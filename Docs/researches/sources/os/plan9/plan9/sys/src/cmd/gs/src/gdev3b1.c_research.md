# File Research: sources/os/plan9/plan9/sys/src/cmd/gs/src/gdev3b1.c

AT&T 3B1/7300/UnixPC console display device.

Key points:
- Defines a display device `gs_att3b1_device` that renders a full page into an in-memory 1-bit screen buffer.
- Opens `/dev/tty`, validates it as a console window with `WIOCGETD`, and allocates a page-sized bitmap buffer.
- Implements device procs for open, close, fill rectangle, copy mono, and output page.
- `att3b1_fill_rectangle` and `att3b1_copy_mono` manipulate the packed bitmap buffer directly using masks, bit reversal, rotation, and logical operations.
- `att3b1_do_output_page` saves/restores window state, changes terminal mode, copies the rendered page into the visible screen window with `WIOCRASTOP`, and lets the user scroll/pan/invert/help/exit via keyboard controls.
- Handles arrow/help/cancel/next escape sequences in `getKeyboard`.
- Optional `ATT3B1_PERF` environment variables can disable output/fill/copy sections for profiling.

Dependencies and interactions:
- Includes Ghostscript device headers plus legacy UnixPC headers `<sys/window.h>` and `<sys/termio.h>`.
- Uses low-level `open`, `close`, `read`, `write`, and `ioctl`.

OS/filesystem relevance:
- Strong OS-device interaction through `/dev/tty`, terminal ioctls, and window raster operations.
- Not portable Plan 9 code; this is for AT&T UnixPC console hardware.
