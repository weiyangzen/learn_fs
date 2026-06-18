# File Research: sources/os/plan9/plan9/sys/src/cmd/gs/libpng/pngget.c

## Summary

`pngget.c` is libpng 1.2.8 getter API implementation for values stored in `png_info` and selected state stored in `png_struct`. It is a read-only accessor layer: most functions validate `png_ptr` / `info_ptr`, check a chunk-validity bit where appropriate, populate caller-provided output pointers, and return either a `PNG_INFO_*` bit, a count, or zero/null on absence.

This file is not filesystem logic. It is bundled third-party PNG metadata access code inside the Plan 9 Ghostscript tree.

## General Pattern

Most getters follow this shape:

- Return `0`, `NULL`, or equivalent if required pointers are missing.
- Check `info_ptr->valid & PNG_INFO_*` for chunk-backed metadata.
- Assign output pointer parameters only when non-null.
- Return the corresponding `PNG_INFO_*` flag, a boolean-like `1`, a byte/count value, or a pointer.

Debug logging uses `png_debug1` in many chunk getter paths.

## Basic Image Accessors

Always-available accessors:

- `png_get_valid`: returns `info_ptr->valid & flag`.
- `png_get_rowbytes`: returns `info_ptr->rowbytes`.
- `png_get_channels`: returns `info_ptr->channels`.
- `png_get_signature`: returns `info_ptr->signature`.

Conditional accessors:

- `png_get_rows` under `PNG_INFO_IMAGE_SUPPORTED`.
- Easy IHDR-style accessors under `PNG_EASY_ACCESS_SUPPORTED`:
  - `png_get_image_width`
  - `png_get_image_height`
  - `png_get_bit_depth`
  - `png_get_color_type`
  - `png_get_filter_type`
  - `png_get_interlace_type`
  - `png_get_compression_type`

These are direct field reads with null guards.

## Resolution and Offset Accessors

Resolution functions read `pHYs` metadata when `PNG_pHYs_SUPPORTED` is enabled:

- `png_get_x_pixels_per_meter`
- `png_get_y_pixels_per_meter`
- `png_get_pixels_per_meter`
- `png_get_pixel_aspect_ratio` under floating-point support
- inch conversion helpers under `PNG_INCH_CONVERSIONS && PNG_FLOATING_POINT_SUPPORTED`
- `png_get_pHYs`
- `png_get_pHYs_dpi`

Behavior details:

- Per-meter getters return `0` unless the `pHYs` chunk is valid and uses meter units.
- `png_get_pixels_per_meter` additionally requires equal x/y density.
- `png_get_pixel_aspect_ratio` returns `y_pixels_per_unit / x_pixels_per_unit`, guarding x density of zero.
- Inch conversion helpers call meter/micron getters and apply fixed conversion constants.
- `png_get_pHYs` returns `PNG_INFO_pHYs` bits for whichever output fields it actually fills.
- `png_get_pHYs_dpi` optionally converts meter units to DPI when `unit_type == 1`.

Offset functions read `oFFs` metadata when `PNG_oFFs_SUPPORTED` is enabled:

- `png_get_x_offset_microns`
- `png_get_y_offset_microns`
- `png_get_x_offset_pixels`
- `png_get_y_offset_pixels`
- `png_get_oFFs`

They require the corresponding offset unit type for the scalar convenience getters.

## Chunk Metadata Accessors

The file implements getters for common ancillary chunks:

- `png_get_bKGD`: returns pointer to `info_ptr->background`.
- `png_get_cHRM`: returns floating chromaticity values.
- `png_get_cHRM_fixed`: returns fixed-point chromaticity values.
- `png_get_gAMA`: returns floating gamma.
- `png_get_gAMA_fixed`: returns fixed-point gamma.
- `png_get_sRGB`: returns rendering intent.
- `png_get_iCCP`: returns profile name, compression type, profile pointer, and profile length.
- `png_get_sPLT`: returns suggested palette array and count.
- `png_get_hIST`: returns histogram pointer.
- `png_get_oFFs`: returns offset x/y/unit.
- `png_get_pCAL`: returns calibration purpose/range/type/units/params.
- `png_get_sCAL`: returns floating physical scale.
- `png_get_sCAL_s`: returns string/fixed build scale fields.
- `png_get_PLTE`: returns palette pointer and palette count.
- `png_get_sBIT`: returns significant bits structure.
- `png_get_text`: returns text array and count.
- `png_get_tIME`: returns modification time.
- `png_get_tRNS`: returns transparency data, with palette/non-palette behavior split.
- `png_get_unknown_chunks`: returns unknown chunk array and count.

Most return the chunk's `PNG_INFO_*` bit when valid and all mandatory output pointers are provided.

## IHDR Validation Getter

`png_get_IHDR` is more than a plain getter. It copies IHDR fields and validates basic sanity:

- Requires non-null `width`, `height`, `bit_depth`, and `color_type`.
- Calls `png_error` for invalid bit depth outside `1..16`.
- Calls `png_error` for invalid color type greater than `6`.
- Calls `png_error` for zero or too-large width/height.
- Warns when width is too large for libpng row processing calculations.
- Optionally returns compression, filter, and interlace type.

It returns `1` on successful field retrieval and `0` on missing required pointers.

## Runtime State Accessors

These read `png_struct` state rather than chunk metadata:

- `png_get_rgb_to_gray_status`
- `png_get_user_chunk_ptr`
- `png_get_compression_buffer_size`
- `png_get_asm_flags`
- `png_get_mmx_bitdepth_threshold`
- `png_get_mmx_rowbytes_threshold`
- `png_get_user_width_max`
- `png_get_user_height_max`

They use null-safe ternary patterns and return zero/null defaults.

## Assembly/MMX Capability Accessors

Under non-1.0 compatibility and assembler support:

- `png_get_asm_flags`: returns current `png_ptr->asm_flags`.
- `png_get_asm_flagmask`: returns theoretically settable read-side MMX flags for selected read operations.
- `png_get_mmx_flagmask`: same idea for MMX flags and optionally reports compiler ID:
  - `1` for MSVC path (`PNG_USE_PNGVCRD`)
  - `2` for gcc/gas path (`PNG_USE_PNGGCCRD`)
  - `-1` otherwise

The flags include:

- `PNG_ASM_FLAG_MMX_READ_COMBINE_ROW`
- `PNG_ASM_FLAG_MMX_READ_INTERLACE`
- `PNG_ASM_FLAG_MMX_READ_FILTER_SUB`
- `PNG_ASM_FLAG_MMX_READ_FILTER_UP`
- `PNG_ASM_FLAG_MMX_READ_FILTER_AVG`
- `PNG_ASM_FLAG_MMX_READ_FILTER_PAETH`

Write-side MMX flags are commented out as future/not implemented.

## Edge Cases and Risks

Most functions are defensive, but there are consistency risks typical of this older libpng code:

- `png_get_sPLT` returns `info_ptr->splt_palettes_num` even if `info_ptr` is null; only the optional output assignment is guarded.
- `png_get_unknown_chunks` similarly returns `info_ptr->unknown_chunks_num` even if `info_ptr` is null.
- `png_get_PLTE` checks `palette != NULL` but writes `*num_palette` without checking `num_palette`.
- Several getters require all output pointers to be non-null before returning data, while others allow partial output. Callers must follow each API's exact contract.
- Returned pointers generally alias storage owned by `png_info` or `png_struct`; callers must not free or outlive the owning libpng structs.

## Dependencies

Direct include:

- `png.h`

Core data dependencies:

- `png_structp`
- `png_infop`
- `png_info` chunk fields
- libpng feature macros for optional chunks and compatibility modes
- `png_debug1`, `png_error`, `png_warning`

## Research Notes

This file is a stable accessor layer for old libpng metadata. It has little algorithmic complexity except `png_get_IHDR` validation and unit conversion helpers. Maintenance should preserve libpng API compatibility, especially return semantics and conditional compilation around optional PNG chunks.
