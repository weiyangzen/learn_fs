# File Research: sources/os/plan9/plan9/sys/src/cmd/gs/src/dxmain.c

GTK+ Ghostscript shared-library front end with display-device callbacks.

Key points:
- Builds a graphical `libgs` client using `gsapi_new_instance`, `gsapi_set_stdio`, `gsapi_set_display_callback`, `gsapi_init_with_args`, and `gsapi_run_string`.
- Registers stdin/stdout/stderr callbacks; stdin is integrated with the GTK/GDK event loop via `gdk_input_add`.
- Implements a `display_callback` for the Ghostscript display device: open, preclose, close, presize, size, sync, page, update, and separation callbacks.
- Maintains a linked list of `IMAGE` objects keyed by Ghostscript handle/device.
- Creates GTK windows, scrolled drawing areas, and optional CMYK/DeviceN separation controls.
- Converts Ghostscript raster formats into GdkRgb-friendly buffers for native 8-bit, 16-bit RGB/BGR, RGB with alpha padding, CMYK, and DeviceN separations.
- Adds a default `-dDisplayFormat=` argument requesting big-endian 8-bit RGB display output.
- Maps Ghostscript exit codes to process exit status, treating `e_Quit` as normal.

Dependencies and interactions:
- Depends on GTK/GDK, Ghostscript public API headers `iapi.h`, `ierrors.h`, and display-device constants from `gdevdsp.h`.
- Receives raster memory owned by Ghostscript; it allocates only conversion buffers and UI structures.
- DeviceN separation names and CMYK component values come through `display_separation`.

OS/filesystem relevance:
- Uses POSIX `read`, `fileno`, stdio writes, and dynamic GUI event handling.
- No Plan 9 filesystem/VFS behavior; this is a GUI client embedded in the Plan 9 Ghostscript tree.
