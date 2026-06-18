# File Research: sources/os/plan9/9front/sys/src/cmd/gs/libpng/pngvcrd.c

Implements a Microsoft Visual C++ inline-assembly, x86/MMX accelerated read-side helper set for libpng 1.2.8.

Key points:
- Compiles only when `PNG_ASSEMBLER_CODE_SUPPORTED` and `PNG_USE_PNGVCRD` are defined.
- `png_mmx_support()` probes CPUID/MMX support using MSVC `_asm`, caches the result in `mmx_supported`, and returns whether MMX is available.
- `png_combine_row()` combines an interlaced/progressive row into the destination row:
  - Fast-copies full rows when `mask == 0xff`.
  - Handles packed 1/2/4-bit pixels in C with optional `PNG_PACKSWAP`.
  - Uses MMX paths for common byte depths including 8, 16, 24, 32, and 48 bits, with C fallback paths keyed by Adam7 pass offsets.
- `png_do_read_interlace()` expands reduced Adam7 pass rows in-place:
  - Packed 1/2/4-bit rows are expanded bitwise.
  - Byte-oriented rows use MMX-specialized duplication loops for 1, 2, 3, and 4 bytes per pixel where possible.
  - 6-byte and uncommon pixel sizes fall back to C copy loops.
  - Updates `row_info->width` and `row_info->rowbytes` to the expanded final width.
- Defines aligned global masks used by filter decoders: `LBCarryMask`, `HBClearMask`, `ActiveMask`, `ActiveMask2`, `ActiveMaskEnd`, `ShiftBpp`, and `ShiftRem`.
- Provides MMX versions of PNG row filter reversal:
  - `png_read_filter_row_mmx_avg()`
  - `png_read_filter_row_mmx_paeth()`
  - `png_read_filter_row_mmx_sub()`
  - `png_read_filter_row_mmx_up()`
- `png_read_filter_row()` dispatches the five PNG filter types:
  - `NONE` leaves the row unchanged.
  - `SUB`, `UP`, `AVG`, and `PAETH` use MMX when enabled by `asm_flags`, bit-depth threshold, and rowbyte threshold; otherwise they use portable C implementations.
  - Unknown filter values generate a warning and clear the filter byte.
- The code preserves older `PNG_1_0_X` behavior with direct `mmx_supported` checks and newer 1.2-style `png_ptr->asm_flags`.

Dependencies and interactions:
- Depends on `png.h`, `png_struct` row state, row filter constants, transformation flags, and Adam7 pass metadata.
- Interacts with libpng read paths that call `png_combine_row`, `png_do_read_interlace`, and `png_read_filter_row`.
- Uses `png_warning`, `png_debug*`, `png_memcpy`, and row metadata macros such as `PNG_ROWBYTES`.

Research relevance:
- This is a legacy platform acceleration layer, not the portable baseline implementation.
- It is tightly coupled to x86, MSVC inline assembly, MMX register cleanup via `emms`, row alignment assumptions, and libpng 1.2 assembly feature flags.
- Notable risk area: some specialized MMX/tail loops are hand-written per pixel depth; the 48-bit combine-row leftover loop appears especially delicate because it operates with 32-bit moves/4-byte advances in a 6-byte-per-pixel case.
