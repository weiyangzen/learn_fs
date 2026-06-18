# File Research: sources/os/plan9/plan9/sys/src/cmd/gs/libpng/pngrtran.c

## Purpose

`pngrtran.c` implements libpng reader-side transformations. Applications configure desired output behavior before reading image rows, and this file updates metadata, precomputes tables, and rewrites decompressed rows in place.

This is libpng 1.2.8 third-party image transformation code vendored under Plan 9's Ghostscript tree.

## Main Responsibilities

- Configure read transformations requested by applications.
- Configure CRC handling policy.
- Initialize background, gamma, palette, and dithering state before row reads.
- Update `png_info` to reflect transformed output format.
- Apply transformation pipeline to each decoded row.
- Implement individual pixel/row transformations for packing, expansion, alpha, gamma, background, color conversion, dithering, and MNG intrapixel undo.

## Public Configuration Functions

Important API entry points include:

- `png_set_crc_action()`: selects behavior for critical and ancillary CRC errors.
- `png_set_background()`: enables alpha/tRNS compositing over a supplied background and records background gamma type.
- `png_set_strip_16()`: converts 16-bit samples to 8-bit.
- `png_set_strip_alpha()`: drops alpha channels.
- `png_set_dither()`: configures palette reduction/dither lookup tables.
- `png_set_gamma()`: enables gamma correction when file/screen gamma require it.
- `png_set_expand()`, `png_set_palette_to_rgb()`, `png_set_gray_1_2_4_to_8()`, `png_set_tRNS_to_alpha()`: enable expansion transformations.
- `png_set_gray_to_rgb()`: expands grayscale to RGB.
- `png_set_rgb_to_gray()` / `_fixed()`: converts RGB to grayscale with configurable coefficients and warning/error behavior.
- `png_set_read_user_transform_fn()`: registers a user row transform callback when compiled in.
- `png_build_grayscale_palette()`: builds a grayscale palette for a given bit depth.

## Initialization

`png_init_read_transformations()` prepares transform state before row decoding.

It can:

- Expand background colors from low-bit grayscale or palette index form.
- Invert palette transparency if alpha inversion is requested before expansion.
- Preserve `background_1` for linear-gamma compositing.
- Disable gamma transformation for palette images with only fully transparent/opaque tRNS entries when file and screen gamma are effectively reciprocal.
- Build gamma tables.
- Pre-apply gamma/background transformations to palette entries.
- Shift palette entries according to significant-bit metadata.

`png_read_transform_info()` updates `info_ptr` metadata so callers see the transformed output layout. It adjusts color type, bit depth, alpha presence, channels, pixel depth, and rowbytes after requested transforms.

## Row Transformation Pipeline

`png_do_read_transformations()` applies row operations in a deliberately ordered sequence:

1. Expand palette/low-bit/tRNS data.
2. Strip alpha if requested.
3. Convert RGB to grayscale.
4. Convert grayscale to RGB early if needed for non-gray background compositing.
5. Composite alpha or transparency against background.
6. Apply gamma correction when not already handled during background compositing.
7. Chop 16-bit samples to 8-bit.
8. Dither to palette.
9. Invert monochrome.
10. Unshift significant bits.
11. Unpack low-bit samples.
12. Convert RGB byte order to BGR.
13. Swap packed bit order.
14. Convert grayscale to RGB late when background is gray.
15. Add filler bytes.
16. Invert alpha.
17. Swap alpha channel position.
18. Swap byte order for 16-bit samples.
19. Run a user transform callback and update row metadata.

The comments warn that this order is sensitive.

## Individual Transform Implementations

The file implements many in-place row transforms:

- `png_do_unpack()`: expands 1/2/4-bit packed samples into one byte per pixel.
- `png_do_unshift()`: shifts samples back to significant-bit ranges.
- `png_do_chop()`: reduces 16-bit samples to 8-bit, optionally using an accurate scale approximation.
- `png_do_read_swap_alpha()`: converts RGBA to ARGB and GA to AG for 8-bit and 16-bit rows.
- `png_do_read_invert_alpha()`: changes alpha convention by subtracting alpha bytes from max.
- `png_do_read_filler()`: inserts filler before or after grayscale/RGB samples.
- `png_do_gray_to_rgb()`: expands gray/gray-alpha rows to RGB/RGBA.
- `png_do_rgb_to_gray()`: computes grayscale from RGB/RGBA using integer coefficients, optionally with gamma tables.
- `png_do_background()`: composites tRNS or alpha over a background for grayscale, RGB, gray-alpha, and RGBA at multiple bit depths.
- `png_do_gamma()`: applies gamma tables to color channels while skipping alpha.
- `png_do_expand_palette()`: expands palette indices to RGB/RGBA using palette and tRNS arrays.
- `png_do_expand()`: expands low-bit grayscale to 8-bit and expands tRNS into alpha for gray/RGB rows.
- `png_do_dither()`: maps RGB/RGBA rows to palette indices or remaps existing palette indices.
- `png_do_read_intrapixel()`: undoes MNG intrapixel differencing for RGB/RGBA rows.

## Dithering and Palette Reduction

`png_set_dither()` has two paths:

- With histogram data, it removes least-used palette entries and builds remapping tables.
- Without histogram data, it repeatedly finds close color pairs and eliminates colors until the palette fits `maximum_colors`.

For full RGB dithering, it builds a reduced color-cube lookup table using `PNG_DITHER_RED_BITS`, `PNG_DITHER_GREEN_BITS`, and `PNG_DITHER_BLUE_BITS`.

Temporary structures include `dither_sort`, `dither_index`, `palette_lookup`, `index_to_palette`, and `palette_to_index`.

## Gamma Tables

`png_build_gamma_table()` builds 8-bit or segmented 16-bit lookup tables.

For 8-bit input it can allocate:

- `gamma_table`
- `gamma_to_1`
- `gamma_from_1`

For 16-bit input it segments tables by `gamma_shift` so each allocation stays below historical 64K constraints:

- `gamma_16_table`
- `gamma_16_to_1`
- `gamma_16_from_1`

The function accounts for significant bits and for future 16-to-8 reduction to reduce table size.

## Background Compositing

`png_do_background()` is one of the largest routines in the file. It handles:

- Low-bit grayscale tRNS replacement.
- 8-bit and 16-bit grayscale tRNS replacement.
- 8-bit and 16-bit RGB tRNS replacement.
- Gray-alpha compositing to gray.
- RGBA compositing to RGB.
- Optional gamma-aware compositing using linearized gamma tables.

After compositing alpha-bearing rows, it removes the alpha channel and updates row metadata.

## Notable Observations

- The code is very compile-time-feature driven; many functions only exist when corresponding `PNG_READ_*_SUPPORTED` macros are enabled.
- Most transforms mutate the row buffer in place and update `row_info` immediately.
- Many operations work backwards from the end of the row when expanding data to avoid overwriting unread source bytes.
- The transform code assumes row buffers have already been allocated large enough for the maximum transformed row size by row setup logic elsewhere.
- `png_correct_palette()` is marked as currently unused but remains available under `PNG_READ_DITHER_SUPPORTED && PNG_CORRECT_PALETTE_SUPPORTED`.

## Research Notes

This file is the main reader-side pixel conversion engine. Sequential and progressive readers both call into it after row filtering, so behavioral changes here affect all libpng read modes in this vendored tree.
