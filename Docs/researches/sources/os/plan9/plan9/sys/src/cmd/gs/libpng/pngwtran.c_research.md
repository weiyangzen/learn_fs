# File Research: sources/os/plan9/plan9/sys/src/cmd/gs/libpng/pngwtran.c

## Summary

`pngwtran.c` implements libpng 1.2.8 write-side row transformations. These transformations convert caller-provided row data into PNG-ready byte order, packing, alpha representation, channel order, and optional MNG intrapixel-differencing form before row filtering/compression.

This is not filesystem or storage code. It is third-party PNG encoder transform code vendored in Plan 9's Ghostscript `libpng` copy.

## Main Compile-Time Gates

The file is active under `PNG_WRITE_SUPPORTED`.

Individual transforms are gated by:

- `PNG_WRITE_USER_TRANSFORM_SUPPORTED`
- `PNG_WRITE_FILLER_SUPPORTED`
- `PNG_WRITE_PACKSWAP_SUPPORTED`
- `PNG_WRITE_PACK_SUPPORTED`
- `PNG_WRITE_SWAP_SUPPORTED`
- `PNG_WRITE_SHIFT_SUPPORTED`
- `PNG_WRITE_INVERT_ALPHA_SUPPORTED`
- `PNG_WRITE_SWAP_ALPHA_SUPPORTED`
- `PNG_WRITE_BGR_SUPPORTED`
- `PNG_WRITE_INVERT_SUPPORTED`
- `PNG_MNG_FEATURES_SUPPORTED`

## Main Dispatcher

`png_do_write_transformations(png_structp png_ptr)` applies transformations in a fixed order:

1. User write transform callback.
2. Strip filler bytes.
3. Pack bit order swap.
4. Pack 8-bit-per-pixel grayscale/palette samples down to 1/2/4 bits.
5. Swap 16-bit byte order.
6. Shift sample values to PNG bit depth.
7. Invert alpha.
8. Swap alpha position.
9. Swap BGR to RGB.
10. Invert monochrome pixels.

Order matters because each transform updates or depends on `png_ptr->row_info`.

## Packing

`png_do_pack(png_row_infop row_info, png_bytep row, png_uint_32 bit_depth)` packs one-channel 8-bit rows into PNG bit depths 1, 2, or 4.

Behavior:

- 1-bit: emits one bit per nonzero source byte.
- 2-bit: emits low two bits of each source byte.
- 4-bit: emits low four bits of each source byte.
- Updates `row_info->bit_depth`, `pixel_depth`, and `rowbytes`.

This path is used for grayscale and paletted images where callers supply unpacked one-byte pixels.

## Sample Shifting

`png_do_shift(png_row_infop row_info, png_bytep row, png_color_8p bit_depth)` scales significant sample bits into the full PNG sample width.

Behavior:

- Skips palette images.
- Determines per-channel shift starts and repeat widths from `png_color_8`.
- Handles sub-8-bit grayscale by expanding within packed bytes.
- Handles 8-bit rows byte by byte.
- Handles 16-bit rows by reconstructing two-byte samples, repeating significant bits into the output value, and writing big-endian sample bytes.

This is used when input samples have fewer significant bits than the PNG output bit depth.

## Alpha Position Swap

`png_do_write_swap_alpha(png_row_infop row_info, png_bytep row)` moves alpha from a leading position to PNG's trailing position.

Supported conversions:

- 8-bit RGBA: ARGB to RGBA.
- 16-bit RGBA: AARRGGBB to RRGGBBAA.
- 8-bit gray-alpha: AG to GA.
- 16-bit gray-alpha: AAGG to GGAA.

It operates in place by reading and writing through paired source/destination pointers.

## Alpha Inversion

`png_do_write_invert_alpha(png_row_infop row_info, png_bytep row)` converts alpha values by subtracting from 255 byte-wise.

Supported cases:

- 8-bit RGBA.
- 16-bit RGBA, inverting both alpha bytes independently.
- 8-bit gray-alpha.
- 16-bit gray-alpha, inverting both alpha bytes independently.

This supports APIs where alpha may represent transparency rather than opacity.

## MNG Intrapixel Differencing

`png_do_write_intrapixel(png_row_infop row_info, png_bytep row)` is enabled under `PNG_MNG_FEATURES_SUPPORTED`.

It applies MNG filter method 64 intrapixel differencing to color rows:

- For 8-bit RGB/RGBA, subtract green from red and blue bytes.
- For 16-bit RGB/RGBA, reconstruct 16-bit red/green/blue samples, subtract green from red and blue modulo 16 bits, and write results back as big-endian bytes.

It only applies to RGB or RGBA rows and returns for unsupported color layouts.

## Dependencies

This file relies on shared transform helpers declared elsewhere in libpng:

- `png_do_strip_filler`
- `png_do_packswap`
- `png_do_swap`
- `png_do_bgr`
- `png_do_invert`

It also depends on `png_struct` transformation flags, `png_row_info`, `png_color_8`, and `PNG_ROWBYTES`.

## Research Notes

`pngwtran.c` is the write-side transform layer called by `png_write_row` before filter selection and compression. It mutates row buffers in place and updates row metadata when packing changes the byte layout. The highest-risk behavior is transform ordering and exact row metadata maintenance after packing or shifting.
