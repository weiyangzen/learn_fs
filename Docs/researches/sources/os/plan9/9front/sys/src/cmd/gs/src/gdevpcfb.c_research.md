# File Research: sources/os/plan9/9front/sys/src/cmd/gs/src/gdevpcfb.c

## Purpose

`gdevpcfb.c` implements Ghostscript display devices for IBM PC EGA/VGA/SuperVGA 16-color planar framebuffers. Unlike the file-output devices in this group, this code talks directly to PC graphics hardware registers and frame-buffer memory through abstractions declared in `gdevpcfb.h`.

## Devices and Setup

The file defines `gs_ega_device`, `gs_vga_device`, and `gs_svga16_device`, with mode-specific dimensions and video mode numbers. `ega_open` adjusts Ghostscript resolution to the selected display mode, saves the current BIOS/text state if needed, installs signal handling through `pcfb_set_signals`, switches hardware mode through `pcfb_set_mode`, and enables all sequencer maps. `ega_close` restores the saved BIOS state.

`svga16_get_params` and `svga16_put_params` expose a `DisplayMode` parameter. Changing the mode while open closes the device before storing the new mode.

## Color Mapping

The file supports build-time selection of monochrome, 8-color, or 16-color EGA behavior through `ega_bits_of_color`. The default maps through the PC 4-bit mapping from `gdevpccm.c`. Lower-color modes mask high RGB bits and decode to half-intensity values.

## Rendering Operations

The implementation uses EGA/VGA planar graphics-register operations. Helper routines such as `memsetcol`, `memsetrect`, `memrwcol`, `memrwcol0`, and `memrwcol2` have optional assembly implementations and C fallbacks. They operate through a `rop_params` structure known to assembly code.

`ega_copy_mono` is the most complex operation. It handles all combinations of zero/one colors being black, white, transparent, or arbitrary EGA colors, selecting AND/OR/XOR/write modes and sometimes doing two passes. It clips input, computes left/right bit masks, accounts for source/destination bit alignment, and uses graphics-register masks to update planar pixels.

`ega_copy_color` copies 4-bit chunky pixels into planar hardware using fill mode and per-bit graphics masks. `ega_fill_rectangle` fills rectangles, optimized for one-row cases by `fill_row_only` and otherwise by `fill_rectangle`. `ega_tile_rectangle` directly handles only simple aligned monochrome tiles with non-transparent colors and no phase offsets; other cases fall back to `gx_default_tile_rectangle`.

`ega_get_bits` reads one scan line back by selecting each hardware plane, copying plane bytes, and combining them into packed 4-bit pixel output using a lookup table.

## Dependencies

The file depends on Ghostscript core/device APIs, parameter lists, PC color mapping, and the platform-specific framebuffer/port abstractions in `gdevpcfb.h`. External functions such as `pcfb_get_state`, `pcfb_set_state`, and `pcfb_set_mode` are platform-specific.

## Filesystem Relevance

No filesystem code is present. The file performs hardware display I/O, not file I/O.

## Risks and Notes

This is low-level, hardware-specific code. It assumes EGA/VGA planar semantics, a maximum width of 800 pixels in `ega_get_bits`, little-endian assembly of readback data, and correct platform port-access privileges. Register state must be restored after operations; missing a `dot_end`, map reset, or graphics-function reset could corrupt subsequent drawing.
