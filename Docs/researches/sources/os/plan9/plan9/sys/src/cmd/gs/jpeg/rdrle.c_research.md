# File Research: sources/os/plan9/plan9/sys/src/cmd/gs/jpeg/rdrle.c

IJG `cjpeg` source adapter for Utah Raster Toolkit RLE files, compiled only under `RLE_SUPPORTED`.

Main structures and modes:

- `rle_source_struct` wraps `cjpeg_source_struct`, an `rle_hdr`, a virtual sample array, a row counter, temporary `rle_pixel **` rows, and an `rle_kind`.
- Supported visual classes are grayscale, mapped grayscale, pseudocolor, truecolor with colormap, and direct color; alpha is explicitly ignored.
- The code requires 8-bit `JSAMPLE` because it assumes `JSAMPLE` and `rle_pixel` have compatible representations.

Flow:

- `start_input_rle()` calls `rle_get_setup()`, normalizes the RLE x origin, determines color interpretation from `ncolors`/`ncmap`, fills libjpeg image metadata, allocates conversion rows, and requests a virtual array.
- `load_image()` is the first `get_pixel_rows` implementation. It reads the whole RLE stream bottom-up into the virtual array, converts mapped variants through the RLE colormap when needed, clears the alpha channel request, then switches future calls to `get_rle_row()` or `get_pseudocolor_row()`.
- `get_rle_row()` returns rows from the virtual array in JPEG top-down order by decrementing the stored row index.
- `get_pseudocolor_row()` maps one-channel pseudocolor indexes into RGB using three 256-entry colormap planes.

This module depends on the external Utah RLE library and libjpeg virtual arrays to bridge RLE’s lower-left origin to JPEG’s top-left scan order.
