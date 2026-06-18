# File Research: sources/os/plan9/9front/sys/src/cmd/gs/src/gdevsvga.h

## Purpose
Shared declarations for Ghostscript SuperVGA display drivers.

## Main Contents
- Declares common SVGA device procedures such as `svga_close`, color mapping, fill/copy, get/put params, `svga_get_bits`, and `svga_copy_alpha`.
- Defines `mode_info`, mapping width/height pairs to BIOS or chipset mode IDs.
- Defines `gx_device_svga`, extending a Ghostscript device with mode callbacks, page callbacks, palette behavior, raster size, bank/window state, and chipset-specific union fields.
- Provides `svga_color_device` and `svga_device` initialization macros.
- Declares utility functions `svga_init_colors`, `svga_find_mode`, and `svga_open`.

## Dependencies
Requires `gdevpcfb.h` and Ghostscript core device declarations.

## Notable Risks
The structure exposes low-level hardware callbacks and chipset state directly. Correct behavior depends on matching the struct fields to the platform-specific implementation in `gdevsvga.c`.

## Filesystem Relevance
No filesystem logic. This is display-driver support infrastructure.
