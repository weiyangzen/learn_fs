# File Research: sources/os/plan9/plan9/sys/src/cmd/gs/jpeg/wrrle.c

IJG `djpeg` destination adapter for Utah Raster Toolkit RLE output, compiled only under `RLE_SUPPORTED`.

Main behavior:

- Requires 8-bit `JSAMPLE`, matching the RLE library’s `rle_pixel` assumption.
- Validates RLE 16-bit signed dimension limits and restricts output to grayscale or RGB with one or three channels.
- Because RLE stores rows bottom-up, stores decompressor rows in a virtual array and emits them in reverse order during `finish_output_rle()`.
- Converts libjpeg colormaps to RLE `rle_map` format by left-shifting 8-bit samples and stores a `color_map_length` comment when quantized output is used.

Key functions:

- `start_output_rle()` validates image constraints, converts any colormap, initializes the first virtual row buffer, and installs `rle_put_pixel_rows()`.
- `rle_put_pixel_rows()` advances the output buffer to the next virtual row.
- `finish_output_rle()` builds an `rle_hdr`, writes setup/colormap, emits one-channel rows directly or splits interleaved RGB rows into RLE planes, then writes EOF.
- `jinit_write_rle()` allocates the RLE plane work rows and full-image virtual array.

This file is an RLE library bridge for `djpeg`, not Plan 9 storage code.
