# File Research: sources/os/plan9/plan9/sys/src/cmd/gs/src/gdevpccm.c

This file contains shared PC-style color mapping helpers used by EGA/VGA framebuffer and PCX-style devices.

For 4-bit EGA/VGA color, `pc_4bit_map_rgb_color` thresholds each RGB component at half intensity, encodes blue/green/red in bits 0/1/2, and sets the high intensity bit for any non-black color. `pc_4bit_map_color_rgb` decodes those color bits back into full-on/full-off RGB values. The comment notes that Ghostscript’s halftoning expects equal shade counts for each component, so only eight colors are actually used despite the 4-bit code space.

For 8-bit SVGA-style color, `pc_8bit_map_rgb_color` maps RGB into a 6x6x6 color cube, producing 216 usable indices. `pc_8bit_map_color_rgb` decodes those indices using a six-step ramp and maps out-of-range palette entries to black. `pc_write_palette` iterates device color indices, calls the device’s `map_color_rgb`, converts color values to 8-bit components, and writes RGB palette triples to a file.
