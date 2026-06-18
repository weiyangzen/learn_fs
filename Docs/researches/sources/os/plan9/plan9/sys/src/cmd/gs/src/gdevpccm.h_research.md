# File Research: sources/os/plan9/plan9/sys/src/cmd/gs/src/gdevpccm.h

This header declares the shared PC color-mapping interface implemented by `gdevpccm.c`.

It exposes 4-bit EGA/VGA mapping procedures `pc_4bit_map_rgb_color` and `pc_4bit_map_color_rgb`, plus `dci_pc_4bit`, a device color-info macro for three components at four bits with two dither levels per color. It also exposes fixed-palette 8-bit mapping procedures `pc_8bit_map_rgb_color` and `pc_8bit_map_color_rgb`, plus `dci_pc_8bit`, describing three components at eight bits with a 6x6x6 cube. Finally, it declares `pc_write_palette`, used by PCX output to serialize palette entries.

The header requires Ghostscript device definitions from `gxdevice.h`.
