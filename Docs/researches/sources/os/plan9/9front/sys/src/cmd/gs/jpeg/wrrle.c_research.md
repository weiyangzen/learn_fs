# File Research: sources/os/plan9/9front/sys/src/cmd/gs/jpeg/wrrle.c

IJG `djpeg` output module for Utah Raster Toolkit RLE images, compiled when `RLE_SUPPORTED` is enabled.

Main data structures and entry points:
- `rle_dest_struct` extends `djpeg_dest_struct` with a virtual image array, optional RLE colormap, and temporary channel row storage.
- `jinit_write_rle` allocates the destination, computes dimensions, allocates the RLE row work array, and requests a whole-image virtual array.
- `start_output_rle` validates dimensions/colorspace/component count, converts any JPEG colormap to RLE `rle_map` format, points the output buffer at row 0, and installs `rle_put_pixel_rows`.
- `rle_put_pixel_rows` advances the virtual array row for each decompressor scanline.
- `finish_output_rle` writes the RLE header, then emits rows bottom-to-top with `rle_putrow`, followed by `rle_puteof`.

Important behavior:
- Full image buffering is required because RLE stores rows bottom-to-top.
- RLE dimensions are limited to signed 16-bit positive extents.
- Grayscale/pseudocolor use one component; RGB/directcolor use three; alpha is not emitted.
- Quantized output writes a 256-entry colormap, with a `color_map_length` comment recording actual color count.
- Non-8-bit `JSAMPLE` builds are rejected.

Filesystem relevance:
- Sequential output adapter with whole-image buffering. No filesystem internals.
