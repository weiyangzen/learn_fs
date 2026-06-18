# File Research: sources/os/plan9/9front/sys/src/cmd/gs/libpng/pngget.c

## Purpose

`pngget.c` implements libpng 1.2.8 getter APIs for reading fields from `png_struct` and `png_info`. It exposes image metadata, ancillary chunk data, user limits, unknown chunks, text chunks, MMX/assembler capability flags, and simple convenience conversions.

The file is almost entirely API glue: validate pointers and `info_ptr->valid` flags, copy internal fields into caller-provided outputs, and return either `0`, `1`, a chunk-validity flag, or a count.

## Basic Getters

Always-present or broadly enabled getters include:

- `png_get_valid(...)`: returns `info_ptr->valid & flag`.
- `png_get_rowbytes(...)`: returns `info_ptr->rowbytes`.
- `png_get_channels(...)`: returns `info_ptr->channels`.
- `png_get_signature(...)`: returns `info_ptr->signature`.
- `png_get_IHDR(...)`: returns core IHDR fields and validates bit depth, color type, width, and height.

Under `PNG_INFO_IMAGE_SUPPORTED`, `png_get_rows(...)` returns `info_ptr->row_pointers`.

Under `PNG_EASY_ACCESS_SUPPORTED`, easy-access getters return width, height, bit depth, color type, filter type, interlace type, compression type, physical resolution, pixel aspect ratio, offsets, and inch-based conversions.

## Chunk Getters

The file provides getters for common PNG chunks, each guarded by its feature macro:

- `bKGD`: `png_get_bKGD`
- `cHRM`: `png_get_cHRM`, `png_get_cHRM_fixed`
- `gAMA`: `png_get_gAMA`, `png_get_gAMA_fixed`
- `sRGB`: `png_get_sRGB`
- `iCCP`: `png_get_iCCP`
- `sPLT`: `png_get_sPLT`
- `hIST`: `png_get_hIST`
- `oFFs`: `png_get_oFFs`
- `pCAL`: `png_get_pCAL`
- `sCAL`: `png_get_sCAL` or `png_get_sCAL_s`
- `pHYs`: `png_get_pHYs`, plus `png_get_pHYs_dpi` when inch conversions and floating point are enabled
- `PLTE`: `png_get_PLTE`
- `sBIT`: `png_get_sBIT`
- `tEXt`/text family: `png_get_text`
- `tIME`: `png_get_tIME`
- `tRNS`: `png_get_tRNS`
- unknown chunks: `png_get_unknown_chunks`

Most chunk getters check both `png_ptr` and `info_ptr`, verify the corresponding `PNG_INFO_*` valid bit, then populate output pointers if supplied.

## Convenience Conversions

Resolution and offset helpers include:

- pixels per meter getters for X/Y/both
- pixels per inch getters using `pixels_per_meter * .0254 + .5`
- micron-to-inch offset getters using `microns * .00003937`
- `png_get_pixel_aspect_ratio(...)`, returning Y pixels per unit divided by X pixels per unit

These helpers return zero when the relevant chunk is missing, the unit is not the expected meter/micrometer unit, or input pointers are null.

## Runtime/Configuration Getters

The tail of the file exposes runtime and configuration state:

- `png_get_rgb_to_gray_status(...)`
- `png_get_user_chunk_ptr(...)`
- `png_get_compression_buffer_size(...)`
- `png_get_asm_flags(...)`
- `png_get_asm_flagmask(...)`
- `png_get_mmx_flagmask(...)`
- `png_get_mmx_bitdepth_threshold(...)`
- `png_get_mmx_rowbytes_threshold(...)`
- `png_get_user_width_max(...)`
- `png_get_user_height_max(...)`

`png_get_asm_flagmask()` and `png_get_mmx_flagmask()` report theoretically settable read-side MMX flags for combine row, interlace, and the four row filters. `png_get_mmx_flagmask()` can also identify the compiled assembler backend: MSVC, GCC/GAS, or unknown.

## Error And Validation Behavior

`png_get_IHDR()` is stricter than most getters. It calls `png_error()` for invalid bit depth, invalid color type, zero/oversized image dimensions, and warns if the width is too large for libpng row processing.

Most other getters return `0` or `NULL` for missing data. Some return the chunk flag only when they actually wrote at least one caller output.

## Dependencies

This file depends on `png.h` with `PNG_INTERNAL` defined and directly reads fields from `png_struct` and `png_info`, including:

- dimensions and row layout fields
- palette and transparency storage
- color-management chunk values
- physical resolution and offset values
- text and unknown chunk arrays
- assembler/MMX configuration fields
- user width/height limits

## Notable Risks

- `png_get_sPLT()` and `png_get_unknown_chunks()` return counts from `info_ptr` even if `info_ptr` is null, so callers must not pass null there despite the partial guard.
- `png_get_PLTE()` checks `palette != NULL` but writes `*num_palette` without checking `num_palette`.
- Several getters expose internal pointers rather than copies, which matches libpng 1.2 API style but means callers observe libpng-owned storage.
- The assembler/MMX getters are tied to the older libpng 1.2 runtime flag model used by `pnggccrd.c`.
