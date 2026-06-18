# File Research: sources/os/plan9/plan9/sys/src/cmd/gs/src/gdevmac.c

Implements the legacy Classic MacOS `macos` Ghostscript output device, producing QuickDraw PICT data. The file notes this device is superseded by the newer API/DISPLAY device.

The device descriptor `gs_macos_device` uses `gs_mac_procs`, including open/close/sync/output-page, rectangle fill, mono copy, line drawing, alpha copy, parameter get/put, and xfont support. Color depth can be 1, 4, 7, 8, or 24 bits.

`mac_open` allocates and initializes a PICT handle with a fixed header, then patches dimensions and resolution. `mac_sync_output` and `mac_output_page` finalize the current PICT with `OpEndPic` while allowing more drawing. `mac_save_pict` writes a 512-byte PICT file header plus PICT data when `OutputFile` is set.

Drawing operations emit QuickDraw PICT opcodes through macros from `gdevmacpictop.h`. `mac_copy_mono` writes BitsRect/PackBitsRect-style data with foreground/background colors and dither copy modes. `mac_copy_alpha` simulates alpha on white backgrounds by creating a shaded color table.

`mac_put_params` handles `UseExternalFonts`, `BitsPerPixel`, and `OutputFile`, including LockSafetyParams checks. `gsdll_get_pict` exposes the `PicHandle` to callers.

The implementation is platform-specific and depends on Mac Toolbox handles, QuickDraw, and Ghostscript DLL callbacks.
