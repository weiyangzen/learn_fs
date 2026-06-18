# File Research: sources/os/plan9/9front/sys/src/cmd/gs/jpeg/rdcolmap.c

Purpose: implements `djpeg -map file` by reading an external color map from GIF or PPM and installing it into the decompressor.

Key contents:
- Compiled only when `QUANT_2PASS_SUPPORTED` is enabled.
- `add_map_entry()` deduplicates RGB colors and appends them to `cinfo->colormap`.
- `read_gif_map()` reads a GIF global color table from the header/logical screen descriptor.
- PPM helpers: `pbm_getc()` skips comments and `read_pbm_integer()` parses decimal header/sample values.
- `read_ppm_map()` reads text PPM (`P3`) or raw PPM (`P6`) and adds each unique pixel color.
- Public entry: `read_color_map()` allocates maximum colormap storage, dispatches by first byte, and fills `actual_number_of_colors`.

Important behavior:
- GIF support here only reads the global color table for mapping; it is separate from GIF image decoding.
- GIF samples are shifted to match `BITS_IN_JSAMPLE`.
- PPM rescaling is not implemented; `maxval` must equal `MAXJSAMPLE`.
- Duplicate colors are ignored.
- Colormap size is capped at `MAXJSAMPLE + 1`; overflow raises `JERR_QUANT_MANY_COLORS`.
- Bad or unsupported map files raise `JERR_BAD_CMAP_FILE`.

Dependencies:
- `cdjpeg.h`, decompressor memory manager, two-pass quantization support, JPEG error macros.
