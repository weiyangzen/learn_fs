# File Research: sources/os/plan9/plan9/sys/src/cmd/gs/src/gdevsvga.h

Declares the shared interface and device structure for the SuperVGA display drivers implemented in `gdevsvga.c`.

Key behavior:
- Declares common device procedures for open/close-adjacent behavior, palette mapping, rectangle fill, mono/color copy, parameter handling, scan-line readback, and alpha copy.
- Defines `mode_info`, a width/height-to-BIOS-mode lookup entry.
- Defines `gx_device_svga`, extending `gx_device_common` with mode getter/setter callbacks, bank-page callback, palette policy, selected mode, raster size, active page, read/write window numbers, and chipset-specific union state.
- Provides `svga_color_device` and `svga_device` macros for constructing 8-bit SVGA devices with initial 640x480 page geometry and resolution derived from page height.
- Declares utility functions for color initialization, mode lookup, and common open handling.

Dependencies:
- Requires `gdevpcfb.h` and the Ghostscript device procedure macro conventions from `gxdevice.h`.

Research notes:
- The structure deliberately separates common banked-frame-buffer logic from chipset-specific page selection.
- The default device macro maps a screen-sized display into a full-page coordinate space rather than exposing physical monitor DPI.
