# File Research: sources/os/plan9/plan9/sys/src/cmd/gs/libpng/pnggccrd.c

## Summary

`pnggccrd.c` is the GNU C / GNU assembler x86 MMX read-side acceleration file from libpng 1.2.8, vendored under Plan 9's Ghostscript `libpng` copy. It is compiled only when `PNG_USE_PNGGCCRD` is defined and provides optimized implementations for PNG row combination, Adam7 interlace expansion, PNG row filter decoding, and runtime MMX capability detection.

This file is not filesystem or storage logic. Its relevance in this subset is as bundled third-party image decoding code inside the Plan 9 source tree.

## Main Compile-Time Gates

The whole file is guarded by `PNG_USE_PNGGCCRD`.

Important feature gates include:

- `PNG_ASSEMBLER_CODE_SUPPORTED`: enables assembler constants and inline MMX paths.
- `PNG_HAVE_ASSEMBLER_COMBINE_ROW`: exposes `png_combine_row`.
- `PNG_READ_INTERLACING_SUPPORTED` and `PNG_HAVE_ASSEMBLER_READ_INTERLACE`: expose `png_do_read_interlace`.
- `PNG_HAVE_ASSEMBLER_READ_FILTER_ROW`: exposes `png_read_filter_row`.
- `PNG_THREAD_UNSAFE_OK`: enables several MMX filter/combine routines that rely on file-scope scratch globals.
- `PNG_MMX_CODE_SUPPORTED`: enables actual CPUID/MMX probing in `png_mmx_support`.

## Public / Internal Entry Points

- `png_combine_row(png_structp png_ptr, png_bytep row, int mask)`: private libpng read helper for progressive/interlaced row composition.
- `png_do_read_interlace(png_structp png_ptr)`: private helper that expands a decoded Adam7 pass row in place to its full row spacing.
- `png_read_filter_row(png_structp png_ptr, png_row_infop row_info, png_bytep row, png_bytep prev_row, int filter)`: private PNG filter decoder dispatcher.
- `png_mmx_support(void)`: exported with `PNGAPI`; tests CPU support and caches result in `_mmx_supported`.
- `png_squelch_warnings(void)`: private helper that self-assigns globals to suppress unused warnings in assembler builds.

Static MMX helpers under `PNG_THREAD_UNSAFE_OK`:

- `png_read_filter_row_mmx_avg`
- `png_read_filter_row_mmx_paeth`
- `png_read_filter_row_mmx_sub`

MMX helper independent of `PNG_THREAD_UNSAFE_OK` in this file:

- `png_read_filter_row_mmx_up`

## State and Constants

The file defines MMX mask constants for packed-pixel row combination:

- `_mask8_0`
- `_mask16_0`, `_mask16_1`
- `_mask24_0` through `_mask24_2`
- `_mask32_0` through `_mask32_3`
- `_mask48_0` through `_mask48_5`
- `_const4`, `_const6`

It also defines aligned `union uAll` globals for filter math masks and shift counts:

- `_LBCarryMask`
- `_HBClearMask`
- `_ActiveMask`
- `_ActiveMask2`
- `_ActiveMaskEnd`
- `_ShiftBpp`
- `_ShiftRem`

When `PNG_THREAD_UNSAFE_OK` is enabled, the file uses global scratch state:

- `_unmask`
- `_FullLength`
- `_MMXLength`
- `_dif`
- `_patemp`
- `_pbtemp`
- `_pctemp`

Those globals are the main reason many accelerated paths are explicitly thread-unsafe.

`_mmx_supported` starts at `2`, meaning "unknown"; `png_mmx_support()` changes it to `1` or `0`.

## `png_combine_row`

`png_combine_row` merges the newly decoded row in `png_ptr->row_buf + 1` into the destination `row` according to an 8-bit repeating pixel mask.

Control flow:

- If MMX support is still unknown, it calls `png_mmx_support()` and may warn that `asm_flags` were not initialized.
- If `mask == 0xff`, it copies the whole decoded row with `png_memcpy`.
- Otherwise it switches on `png_ptr->row_info.pixel_depth`.

Packed depths `1`, `2`, and `4` are handled in C with bit extraction and bit replacement. These paths honor `PNG_PACKSWAP` when enabled.

Byte-aligned depths use either MMX or C fallback:

- `8`, `16`, `24`, `32`, and `48` bits have MMX combine paths when assembler, thread-unsafe globals, and `PNG_ASM_FLAG_MMX_READ_COMBINE_ROW` allow it.
- `64` bits uses the C fallback only in the read code present here.
- C fallback uses Adam7 pass metadata (`png_pass_start`, `png_pass_inc`, `png_pass_width`) to copy only the active pixel spans and handles leftover pixels after rounding width down to a multiple of 8.

Risk notes:

- The MMX paths assume x86 GNU assembler syntax and careful register constraints.
- The C fallback contains historical bugfixes around final byte count and leftover pixels; changing loop bounds would be risky.
- The `48`-bit MMX leftover cleanup appears to copy only a 32-bit word per pixel in the assembly tail, while the C path handles 6 bytes; the file's own changelog says 48-bit MMX work was incomplete/untested historically.

## `png_do_read_interlace`

`png_do_read_interlace` expands a decoded Adam7 row in place after earlier transformations such as 16-to-8 conversion.

Control flow:

- Reads `row_info`, `row`, and current `pass` from `png_ptr`.
- Computes `final_width = row_info->width * png_pass_inc[pass]`.
- Switches on `row_info->pixel_depth`.

For packed `1`, `2`, and `4` bpp, it walks backward from the end of the packed row, replicating each source pixel into the expanded destination spacing. It accounts for `PNG_PACKSWAP`.

For byte-aligned pixels, it calculates `pixel_bytes = pixel_depth >> 3`, sets source and destination pointers to the last pixel positions, and expands backward to avoid overwriting unread data.

MMX specializations cover several cases:

- 1-byte pixels for pass groups `0/1`, `2/3`, and `4/5`.
- 2-byte pixels for pass groups `0/1`, `2/3`, and `4/5`.
- 3-byte pixels with separate logic for pass groups and a partial MMX cleanup.
- 4-byte pixels for pass groups.
- 8-byte pixels for pass groups.
- 6-byte pixels falls back to C.

After expansion, it updates:

- `row_info->width`
- `row_info->rowbytes`

Risk notes:

- The function operates in place, backward, and depends on exact source/destination pointer arithmetic.
- The file comments explicitly list still-open uncertainty around 24-bit pass `4/5` width handling and testing for 64-bit pixels.
- Debug-only bounds messages use pointer values formatted as integers, which reflects old C style and is not portable.

## PNG Filter Decoding

`png_read_filter_row` is the dispatcher for PNG filter types:

- `PNG_FILTER_VALUE_NONE`: no-op.
- `PNG_FILTER_VALUE_SUB`: reconstructs bytes using left byte.
- `PNG_FILTER_VALUE_UP`: reconstructs bytes using previous row byte.
- `PNG_FILTER_VALUE_AVG`: reconstructs using average of left and previous row.
- `PNG_FILTER_VALUE_PAETH`: reconstructs using Paeth predictor.
- Unknown filter: warns and clears first row byte.

It prefers MMX helpers when all of these are true:

- assembler support is enabled,
- corresponding `png_ptr->asm_flags` bit is set,
- row bit depth and row byte count meet `mmx_bitdepth_threshold` and `mmx_rowbytes_threshold`,
- and for Sub/Avg/Paeth, `PNG_THREAD_UNSAFE_OK` is enabled.

Fallback C implementations are present inline for all filters, so this file no longer depends on a separate C read-filter implementation.

### MMX Sub Filter

`png_read_filter_row_mmx_sub`:

- Computes bytes per pixel (`bpp`) and `_FullLength = rowbytes - bpp`.
- Handles initial bytes up to an 8-byte alignment boundary.
- Uses bpp-specific MMX loops for `1`, `2`, `3`, `4`, `6`, and `8` bytes per pixel.
- Finishes trailing bytes with scalar x86 code and emits `EMMS`.

### MMX Up Filter

`png_read_filter_row_mmx_up`:

- Adds `prev_row` bytes to `row` bytes.
- Aligns to 8 bytes, then uses a heavily unrolled 64-byte MMX loop.
- Handles remaining 8-byte groups and final scalar bytes.
- Saves/restores `ebx` under `__PIC__`.

This is the simplest MMX filter path because it has no left-neighbor dependency.

### MMX Average Filter

`png_read_filter_row_mmx_avg`:

- Handles first `bpp` bytes with prior-row-only averaging.
- Aligns to an 8-byte boundary.
- Uses bpp-specific vector logic for `1`, `2`, `3`, `4`, `6`, and `8` byte pixels.
- Uses `_LBCarryMask` and `_HBClearMask` to compute byte-wise divide-by-two with carry behavior.
- Uses scalar cleanup for trailing bytes.

Risk notes:

- Uses global `_dif`, `_FullLength`, `_MMXLength`, and shift/mask globals.
- Historical comments describe a fixed 16-bit grayscale bug in the `bpp == 2` case.

### MMX Paeth Filter

`png_read_filter_row_mmx_paeth`:

- Handles the first `bpp` bytes as `row += prev_row`.
- Aligns to an 8-byte boundary using scalar predictor logic.
- Uses bpp-specific MMX predictor calculations for `3`, `4`, `6`, and `8` byte pixels.
- Falls back to scalar predictor loops for `1`, `2`, and default bpp.
- Cleans up trailing bytes after MMX processing.

The Paeth MMX code implements vectorized predictor selection by computing absolute differences in word lanes, comparing `pa`, `pb`, and `pc`, and selecting `a`, `b`, or `c`.

Risk notes:

- This is the most complex block in the file.
- It relies on global scratch integers `_patemp`, `_pbtemp`, `_pctemp` in scalar alignment/cleanup paths.
- Correctness depends on exact unsigned byte wraparound behavior after adding predictor values.

## CPU Feature Detection

`png_mmx_support` uses inline assembly to:

- Save `ebx`, `ecx`, and `edx`.
- Test whether the CPU supports toggling the EFLAGS ID bit.
- Call `cpuid`.
- Check CPUID function availability.
- Check EDX bit 23 for MMX.
- Store `1` or `0` into `_mmx_supported`.

If `PNG_MMX_CODE_SUPPORTED` is not defined, it forces `_mmx_supported = 0`.

Risk notes:

- This assumes 32-bit x86 semantics (`pushfl`, `popfl`, `%eax`, `%ebx`, etc.).
- It is unsuitable for non-x86 or 64-bit-only compilers unless excluded by build flags.
- The file avoids declaring `ebx/ecx/edx` as clobbers in this function because it saves/restores them manually.

## Dependencies

Direct include:

- `png.h`

Important libpng data/functions/macros used:

- `png_struct`, `png_row_info`, row buffers and pass fields.
- `png_pass_start`, `png_pass_inc`, `png_pass_width` or local copies.
- `png_memcpy`, `png_warning`, `png_debug`, `png_debug1`, `png_debug2`.
- `PNG_ROWBYTES`.
- `PNG_ASM_FLAG_MMX_READ_*` flags.
- PNG filter constants and transform flags.

## Research Notes

This file is old vendored libpng optimization code. It is performance-oriented, platform-specific, and conditionally thread-unsafe. For maintenance, the safest stance is to treat it as third-party code and avoid local edits unless reproducing a known upstream libpng fix or disabling the assembly path for portability.
