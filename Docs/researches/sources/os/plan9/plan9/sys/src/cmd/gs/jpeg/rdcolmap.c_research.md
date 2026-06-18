# File Research: sources/os/plan9/plan9/sys/src/cmd/gs/jpeg/rdcolmap.c

This file implements `djpeg`'s `-map file` option when `QUANT_2PASS_SUPPORTED` is enabled. It reads an external color map and stores it in `cinfo->colormap` for decompression quantization.

`read_color_map()` allocates a maximum-size 3-component colormap of `MAXJSAMPLE+1` entries, initializes `actual_number_of_colors` to zero, reads the first byte, and dispatches to GIF or PPM parsing.

GIF map handling reads the GIF header and logical screen descriptor after the initial `G`, verifies the `GIF` signature and presence of a global color table, computes its size, then imports RGB triples into the map. Pixel data is not decoded; only the global palette is used.

PPM map handling supports text P3 and raw P6 formats. It reads width, height, and maxval with PBM-style comment skipping, requires `maxval == MAXJSAMPLE`, then reads every pixel and adds unique colors to the map. Duplicate colors are ignored by linear scan.

`add_map_entry()` enforces uniqueness and rejects maps larger than `MAXJSAMPLE+1` colors. Error handling uses libjpeg `ERREXIT` macros with `JERR_BAD_CMAP_FILE` or `JERR_QUANT_MANY_COLORS`.

The file depends on `cdjpeg.h`, stdio input, libjpeg decompressor structures, and two-pass quantization support. It does no filesystem-specific work beyond reading the supplied stdio file.
