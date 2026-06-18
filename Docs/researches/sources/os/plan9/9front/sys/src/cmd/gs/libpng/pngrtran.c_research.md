# File Research: sources/os/plan9/9front/sys/src/cmd/gs/libpng/pngrtran.c

## Role

`pngrtran.c` implements read-side PNG transformation setup and row mutation for libpng 1.2.8. Applications call public setters before reading rows; this file records requested transformations, updates metadata, builds lookup tables, and applies in-place transformations to each decoded row.

## Public Transform Setters

- `png_set_crc_action()` configures CRC behavior for critical and ancillary chunks.
- `png_set_background()` configures alpha/tRNS compositing against a background color.
- `png_set_strip_16()` requests 16-bit samples be reduced to 8-bit.
- `png_set_strip_alpha()` requests alpha removal.
- `png_set_dither()` configures palette reduction or RGB-to-palette lookup tables.
- `png_set_gamma()` configures screen/file gamma correction.
- `png_set_expand()`, `png_set_palette_to_rgb()`, `png_set_gray_1_2_4_to_8()`, and `png_set_tRNS_to_alpha()` all set expansion behavior.
- `png_set_gray_to_rgb()` requests grayscale expansion to RGB.
- `png_set_rgb_to_gray()` / `png_set_rgb_to_gray_fixed()` configure RGB-to-gray conversion and coefficients.
- `png_set_read_user_transform_fn()` installs an application-defined row transform.

## Initialization and Metadata

- `png_init_read_transformations()` prepares transformation state before row decoding:
  - Expands background colors for low-bit-depth gray or palette inputs.
  - Optionally inverts tRNS alpha before expansion.
  - Builds gamma tables when needed.
  - Applies background/gamma corrections to palettes.
  - Shifts palette entries according to significant-bit metadata.
- `png_read_transform_info()` mutates `info_ptr` to match post-transform row format:
  - Color type changes.
  - Bit depth changes.
  - Channel count changes.
  - Pixel depth and rowbytes recalculation.
  - User transform depth/channel overrides.

## Per-Row Transform Pipeline

`png_do_read_transformations()` applies transformations in a carefully ordered sequence:

1. Expand palette/low-bit-depth/tRNS.
2. Strip alpha.
3. RGB-to-gray.
4. Gray-to-RGB before background only when background is non-gray.
5. Background compositing.
6. Gamma correction when not already handled by background.
7. 16-to-8 reduction.
8. Dithering.
9. Monochrome inversion.
10. Significant-bit unshift.
11. Packed-pixel unpacking.
12. BGR conversion.
13. Pack bit-order swap.
14. Gray-to-RGB after background when background is gray.
15. Filler channel insertion.
16. Alpha inversion.
17. Alpha-position swap.
18. Byte swap.
19. User transform callback and row metadata update.

The comments emphasize that this ordering is significant and fragile.

## Internal Row Helpers

- `png_do_unpack()` expands 1/2/4-bit samples into one byte per pixel.
- `png_do_unshift()` shifts samples down to significant bits.
- `png_do_chop()` converts 16-bit samples to 8-bit, optionally with accurate scaling.
- `png_do_read_swap_alpha()` converts RGBA/GA layout to ARGB/AG-style ordering.
- `png_do_read_invert_alpha()` inverts alpha values.
- `png_do_read_filler()` inserts filler bytes/words before or after gray/RGB samples.
- `png_do_gray_to_rgb()` expands gray or gray-alpha rows to RGB/RGBA.
- `png_do_rgb_to_gray()` collapses RGB/RGBA to gray/gray-alpha using configured coefficients, optionally in linear gamma space.
- `png_build_grayscale_palette()` builds synthetic gray palettes.
- `png_correct_palette()` conditionally applies gamma/background correction to palettes.
- `png_do_background()` composites transparency/alpha against configured background for gray, RGB, gray-alpha, and RGBA rows.
- `png_do_gamma()` applies gamma lookup tables to non-alpha samples.
- `png_do_expand_palette()` expands indexed rows to RGB or RGBA.
- `png_do_expand()` expands low-bit-depth gray and converts tRNS to alpha.
- `png_do_dither()` maps RGB/RGBA/palette rows to a reduced palette.
- `png_build_gamma_table()` builds 8-bit or segmented 16-bit gamma lookup tables.
- `png_do_read_intrapixel()` reverses MNG intrapixel differencing for RGB/RGBA rows.

## Memory and Lookup Tables

This file can allocate several substantial structures through `png_malloc()`:

- Dither index arrays.
- Dither sort arrays and temporary hash lists.
- Palette lookup cubes.
- Gamma tables:
  - 8-bit `gamma_table`, `gamma_to_1`, `gamma_from_1`.
  - Segmented 16-bit `gamma_16_table`, `gamma_16_to_1`, `gamma_16_from_1`.

The 16-bit gamma tables are segmented to avoid allocations larger than 64 KiB, matching old libpng portability constraints.

## Dependencies

- Transform flags and structs from `png.h`.
- Allocation wrappers from `pngmem.c`.
- Row buffers initialized by read startup code.
- Math library functions `pow()`, `fabs()` when floating point gamma/background support is enabled.
- PNG macros such as `PNG_ROWBYTES`, `png_composite`, and `png_composite_16`.

## State Mutated

- `png_ptr->transformations`, `flags`, `mode`.
- Background/gamma state: `background`, `background_1`, `gamma`, `screen_gamma`, gamma tables.
- Palette and transparency data.
- Dither lookup/index state.
- RGB-to-gray coefficients/status.
- `row_info` and row buffer contents on every transformed row.
- `info_ptr` metadata during `png_read_transform_info()`.

## Risks and Maintenance Notes

- Most transforms mutate rows in place and often expand from the end backward. Correct row-buffer sizing before transformation is mandatory.
- Transform order is semantically important; moving steps can change alpha compositing, gamma correctness, or row layout.
- Many paths are conditionally compiled, so behavior can differ sharply by build configuration.
- `png_do_rgb_to_gray()` checks warning/error modes using equality against the full `transformations` bitmask in places; combined transform flags may affect whether warning/error actions trigger.
- Dithering without histograms uses a complex nearest-color elimination algorithm with many temporary allocations.
- Gamma correction requires floating-point support in this version; the file notes a missing integer implementation.
- The MNG intrapixel path only applies when MNG feature flags and color row types are enabled.

## Research Summary

This is the main read-transform engine. `pngread.c` and `pngpread.c` decode filtered rows, then call into this file to produce the application-requested row format. It owns the highest-risk pixel mutation logic in this group because it combines pointer arithmetic, in-place buffer expansion/shrinking, gamma/background math, palette handling, and compile-time feature variation.
