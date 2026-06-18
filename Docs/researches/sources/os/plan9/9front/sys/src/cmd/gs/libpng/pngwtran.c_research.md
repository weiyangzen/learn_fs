# File Research: sources/os/plan9/9front/sys/src/cmd/gs/libpng/pngwtran.c

Implements writer-side row transformations applied before PNG filtering and compression.

Key points:
- Compiles under `PNG_WRITE_SUPPORTED`.
- `png_do_write_transformations()` applies transformations in a fixed order:
  - User transform callback.
  - Strip filler.
  - Pack-swap.
  - Pack 8-bit samples down to 1/2/4-bit rows.
  - Swap 16-bit byte order.
  - Shift sample values to declared significant-bit depth.
  - Invert alpha.
  - Swap alpha position.
  - BGR to RGB.
  - Invert monochrome.
- `png_do_pack()` packs one-channel 8-bit grayscale/palette-style samples into 1-, 2-, or 4-bit packed bytes and updates `row_info` bit depth, pixel depth, and rowbytes.
- `png_do_shift()` scales samples so stored PNG values use the full legal range implied by `sBIT`:
  - Handles packed low-bit-depth grayscale rows.
  - Handles 8-bit samples.
  - Handles 16-bit samples.
  - Skips palette color type.
- `png_do_write_swap_alpha()` changes alpha placement:
  - RGB alpha: ARGB to RGBA for 8-bit and AARRGGBB to RRGGBBAA for 16-bit.
  - Gray alpha: AG to GA for 8-bit and AAGG to GGAA for 16-bit.
- `png_do_write_invert_alpha()` converts alpha values by subtracting from 255:
  - Handles RGB-alpha and gray-alpha rows.
  - Handles both 8-bit and 16-bit channel storage, though 16-bit inversion is byte-wise in this legacy implementation.
- `png_do_write_intrapixel()` supports MNG filter method 64 intrapixel differencing:
  - For RGB/RGBA 8-bit rows, stores red and blue as differences from green.
  - For RGB/RGBA 16-bit rows, computes 16-bit red-green and blue-green differences and writes them back big-endian.
  - Applies only to color rows.

Dependencies and interactions:
- Called from `png_write_row()` in `pngwrite.c` after row copying and interlace handling, before filter selection.
- Uses shared transformation helpers from other libpng files for filler stripping, packswap, swap, BGR, and mono inversion.
- Driven by `png_ptr->transformations`, `png_ptr->flags`, `png_ptr->shift`, and `png_ptr->bit_depth`.

Research relevance:
- This file is the writer-side counterpart to read transforms. It mutates row buffers in-place and keeps `row_info` synchronized so subsequent filtering and IDAT compression see the final PNG storage format.
