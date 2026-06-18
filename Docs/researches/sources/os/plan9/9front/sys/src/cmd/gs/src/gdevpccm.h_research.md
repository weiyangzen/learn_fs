# File Research: sources/os/plan9/9front/sys/src/cmd/gs/src/gdevpccm.h

## Purpose

`gdevpccm.h` declares shared EGA/VGA and SVGA color mapping routines for PC-style Ghostscript devices.

## Contents

The header declares `pc_4bit_map_rgb_color`, `pc_4bit_map_color_rgb`, and the `dci_pc_4bit` device color-info macro for a 3-component, 4-bit indexed color model. It also declares `pc_8bit_map_rgb_color`, `pc_8bit_map_color_rgb`, and `dci_pc_8bit` for the fixed 6x6x6 8-bit palette. Finally, it declares `pc_write_palette(gx_device *, uint, FILE *)`.

## Dependencies and Integration

It requires `gxdevice.h` to define `dev_proc_*` macros and Ghostscript device types. Consumers use it to share identical palette behavior between PCX output, 2-up PCX output, and EGA/VGA display code.

## Filesystem Relevance

No filesystem functionality is present.

## Risks and Notes

The macros encode assumptions about component counts, depth, max gray/color, and dither values. Devices using these macros must keep their pixel encodings consistent with the mapping routines.
