# File Research: sources/os/plan9/9front/sys/src/cmd/gs/src/gdevsvga.c

## Purpose
Common Ghostscript SuperVGA display driver implementation for VESA and several 256-color PC SVGA chipsets. It handles banked framebuffer drawing, palette management, mode selection, and chipset-specific page switching.

## Main Concepts
- Shared SVGA procedures: open/close, color mapping, fill, copy mono/color, get bits, alpha copy, and parameter put.
- `gx_device_svga` instances are declared for `vesa`, `atiw`, `tvga`, `tseng`, `cirr`, and `ali`.
- Uses banked VGA memory at segment `0xa000`, with 64K page switching through BIOS or hardware registers.
- Maintains a dynamic palette table starting at color index 64 unless the device uses a fixed palette.

## Key Functions
- `svga_find_mode`, `vesa_find_mode`: choose a mode that fits the requested dimensions and adjust resolution.
- `svga_open`, `svga_close`: save/restore display mode, load DAC colors, initialize page state.
- `svga_map_rgb_color`, `svga_map_color_rgb`: map RGB to fixed cube or dynamic DAC entries and read DAC values back.
- `svga_fill_rectangle`: writes directly into banked framebuffer memory, including boundary-crossing handling.
- `svga_copy_mono`, `svga_copy_color`: raster copy paths for 1-bit and 8-bit source data.
- `svga_get_bits`: reads a scanline back from banked framebuffer memory.
- `svga_copy_alpha`: approximates alpha as saturation toward white and caches shade mappings.
- Chipset page setters: `vesa_set_page`, `atiw_set_page`, `tvga_set_page`, `tseng_set_page`, `cirr_set_page`, `ali_set_page`.

## Dependencies
Uses Ghostscript device internals, PC framebuffer helpers, PC color mapping, BIOS interrupt helpers, port I/O, and chipset register access.

## Notable Risks
- Requires direct BIOS, VGA DAC, and hardware port access; unsuitable for protected modern systems unless emulated.
- Global saved mode and dynamic palette state are process-wide.
- Many hardware operations have no timeout or error confirmation.
- `tseng_open` returns success if `svga_open` fails after mode selection because it returns `0` when `code < 0`.
- Pointer/page arithmetic is tuned for 16-bit segmented/banked VGA memory and is fragile outside that environment.

## Filesystem Relevance
No filesystem logic. This is hardware display output code.
