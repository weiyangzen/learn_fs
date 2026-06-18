# File Research: sources/os/plan9/plan9/sys/src/cmd/gs/libpng/pngvcrd.c

## Summary

`pngvcrd.c` is the Microsoft Visual C++ inline-assembly x86/MMX read-side acceleration file from libpng 1.2.8, vendored under Plan 9's Ghostscript `libpng` copy. It implements CPU MMX detection plus optimized read helpers for row combining, Adam7 interlace expansion, and PNG filter reconstruction.

This is not filesystem or storage code. Its relevance in subset A is as bundled third-party image decoding code inside the Plan 9 source tree.

## Main Compile-Time Gates

The entire file is guarded by:

- `PNG_ASSEMBLER_CODE_SUPPORTED`
- `PNG_USE_PNGVCRD`

Additional feature gates affect individual regions:

- `PNG_READ_INTERLACING_SUPPORTED`: enables `png_do_read_interlace`.
- `PNG_READ_PACKSWAP_SUPPORTED`: changes packed-bit order handling for 1/2/4-bit rows.
- `PNG_1_0_X`: switches between old direct `mmx_supported` decisions and newer `png_ptr->asm_flags`.
- Various `PNG_ASM_FLAG_MMX_*` bits select individual accelerated paths in newer libpng builds.

## Public / Internal Entry Points

- `png_mmx_support(void)`: uses CPUID from MSVC inline assembly to detect MMX support and caches the result in file-scope `mmx_supported`.
- `png_combine_row(png_structp png_ptr, png_bytep row, int mask)`: combines the just-decoded row into the display/output row for interlaced or progressive reads.
- `png_do_read_interlace(png_structp png_ptr)`: expands a decoded Adam7 pass row in place to full pass spacing.
- `png_read_filter_row(png_structp png_ptr, png_row_infop row_info, png_bytep row, png_bytep prev_row, int filter)`: dispatches PNG row-filter reconstruction.
- `png_read_filter_row_mmx_avg`, `png_read_filter_row_mmx_paeth`, `png_read_filter_row_mmx_sub`, `png_read_filter_row_mmx_up`: MMX-specialized filter decoders.

## State and Constants

The file uses `static int mmx_supported = 2`, where `2` means unknown, `1` supported, and `0` unsupported.

It also defines file-scope aligned `union uAll` globals:

- `LBCarryMask`
- `HBClearMask`
- `ActiveMask`
- `ActiveMask2`
- `ActiveMaskEnd`
- `ShiftBpp`
- `ShiftRem`

These globals are written by the filter routines before entering inline assembly. That makes the accelerated code effectively non-reentrant and risky in multithreaded callers if multiple PNG rows are decoded concurrently through the same process.

## Row Combination

`png_combine_row` handles masked row composition.

Behavior:

- If MMX support is unknown, it calls `png_mmx_support()`.
- If `mask == 0xff`, it copies the full decoded row from `png_ptr->row_buf + 1`.
- For 1/2/4-bit pixels, it uses C bit extraction and insertion, honoring `PNG_PACKSWAP`.
- For byte-aligned pixel depths, it uses MMX where enabled and falls back to C Adam7 pass stepping otherwise.

Specialized MMX cases exist for 8, 16, 24, 32, and 48-bit pixel depths. Other depths fall through to generic byte-copy stepping based on the current Adam7 pass.

Risk notes:

- The 48-bit MMX tail path copies and advances by 4 bytes in its leftover loop even though 48-bit pixels are 6 bytes. This matches a historically fragile area also visible in sibling MMX code.
- The routine depends on exact pass offsets and row byte calculations; off-by-one changes can corrupt rows.
- The MSVC `_asm` syntax makes this file non-portable outside 32-bit x86 MSVC-style builds.

## Adam7 Interlace Expansion

`png_do_read_interlace` expands a decoded Adam7 pass row in place.

Behavior:

- Computes `final_width = row_info->width * png_pass_inc[pass]`.
- Handles packed 1/2/4-bit rows in C by walking backward through packed bits.
- Handles byte-aligned rows by walking backward from the last source pixel to the last destination pixel to avoid overwriting unread source bytes.
- Uses MMX specializations for 1, 2, 3, and 4-byte pixels for pass groups `0/1`, `2/3`, and `4/5`.
- Handles 6-byte and other uncommon pixel widths through C fallback loops.

After expansion it updates:

- `row_info->width`
- `row_info->rowbytes`

Risk notes:

- The in-place backward expansion is pointer-arithmetic heavy.
- The file comments mention historical sign fixes for cleanup code after MMX loops.
- Wider pixels and odd leftover widths are the highest-risk paths.

## PNG Filter Decoding

`png_read_filter_row` dispatches PNG filter reconstruction:

- `PNG_FILTER_VALUE_NONE`: no-op.
- `PNG_FILTER_VALUE_SUB`: reconstructs from left bytes.
- `PNG_FILTER_VALUE_UP`: reconstructs from previous-row bytes.
- `PNG_FILTER_VALUE_AVG`: reconstructs from the average of left and previous-row bytes.
- `PNG_FILTER_VALUE_PAETH`: reconstructs from the Paeth predictor.
- Unknown filter values warn and clear the first row byte.

For each filter, newer builds check `png_ptr->asm_flags`, `png_ptr->mmx_bitdepth_threshold`, and `png_ptr->mmx_rowbytes_threshold` before using MMX. Older `PNG_1_0_X` builds use only the cached MMX support result.

### MMX Sub

`png_read_filter_row_mmx_sub` reconstructs bytes by adding each byte to its left neighbor. It aligns to an 8-byte boundary, then uses bpp-specific MMX loops for common byte-per-pixel values, with scalar cleanup.

### MMX Up

`png_read_filter_row_mmx_up` adds each byte from `prev_row` to the current row. It uses an unrolled 64-byte MMX loop, then handles remaining 8-byte groups and final scalar bytes.

### MMX Average

`png_read_filter_row_mmx_avg` reconstructs using PNG Average filter rules. It handles the first `bpp` bytes separately, aligns to 8 bytes, and uses masks to emulate byte-wise average arithmetic without losing carry behavior.

### MMX Paeth

`png_read_filter_row_mmx_paeth` reconstructs with the Paeth predictor. It has complex bpp-specific vector logic for common pixel sizes and scalar fallback for small or uncommon cases.

## Dependencies

This file depends on internal libpng state and helpers from `png.h`:

- `png_struct`, `png_row_info`, row buffers, pass number, width, transformations, and assembler flags.
- `png_memcpy`, `png_warning`, `png_error`, and debug macros.
- PNG filter constants and transform flags.

It is initialized indirectly by `png_init_mmx_flags()` in `png.c`, which is called during read/write struct creation in other libpng files.

## Research Notes

This file is performance-oriented, architecture-specific third-party code. It should be treated as vendored libpng 1.2.8 code rather than native Plan 9 filesystem code. Maintenance risk is high because behavior is encoded in inline assembly, shared scratch globals, and subtle PNG row-layout invariants.
