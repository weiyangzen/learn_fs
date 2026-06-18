# File Research: sources/os/plan9/plan9/sys/src/cmd/gs/libpng/pngconf.h

## Role

`pngconf.h` is libpng’s machine and build configuration header. It decides platform portability settings, feature availability, public typedefs, calling conventions, export macros, memory model macros, and default limits before `png.h` exposes the API.

This file is also not filesystem code. It is infrastructure for building the vendored libpng copy consistently on many C environments, including older DOS/Windows, Cygwin, Mac, OS/2, and generic Unix-like targets.

## Configuration Entry Points

The file defines `PNG_1_2_X` and optionally includes `pngusr.h` if `PNG_USER_CONFIG` is set. That allows downstream builds to override or disable libpng features without editing this file.

It supports `PNG_VERSION_INFO_ONLY`, which bypasses most typedefs and feature setup when only version metadata is needed.

Default core settings include:

- `PNG_ZBUF_SIZE 8192`
- `PNG_READ_SUPPORTED` unless `PNG_NO_READ_SUPPORTED`
- `PNG_WRITE_SUPPORTED` unless `PNG_NO_WRITE_SUPPORTED`
- `PNG_MNG_FEATURES_SUPPORTED` by default for non-1.0 builds
- `PNG_FLOATING_POINT_SUPPORTED` unless explicitly disabled
- `PNG_SETJMP_SUPPORTED` unless disabled
- `PNG_USER_WIDTH_MAX 1000000L`
- `PNG_USER_HEIGHT_MAX 1000000L`

## Platform And Library Includes

The header conditionally includes:

- `stdio.h` unless `PNG_NO_STDIO` or Windows CE limitations apply.
- `sys/types.h` on most non-Mac, non-RISCOS, non-Windows CE platforms.
- `setjmp.h` for libpng fatal error recovery.
- `string.h` or `strings.h`.
- `stdlib.h` and `math.h`/Mac `fp.h` only under `PNG_INTERNAL`.
- `time.h` if `PNG_tIME_SUPPORTED`.

For Linux with `_BSD_SOURCE`, it temporarily undefines `_BSD_SOURCE` around `setjmp.h` to force the desired setjmp behavior.

## Feature Matrix

The bulk of the file maps `PNG_NO_*` and `*_NOT_SUPPORTED` macros into positive `*_SUPPORTED` macros. Important default behavior:

- Read transforms are enabled by default: expand, shift, pack, BGR, swap, packswap, invert, dither, background, 16-to-8, filler, gamma, gray-to-RGB, alpha swaps/inversion/strip, user transform, RGB-to-gray.
- Progressive read support is enabled by default.
- Read interlacing support is always defined for PNG-compliant decoders.
- Write transforms are enabled by default: shift, pack, BGR, swap, packswap, invert, filler, alpha swaps/inversion, user transform.
- Write interlacing and flush support are enabled by default.
- Weighted filtering is enabled when floating point is available.
- Error-number support is enabled for non-1.0 builds.
- User memory callbacks and user limits are enabled for non-1.0 builds.

Ancillary chunk support is also enabled by default for read and write unless disabled as a group or per chunk. Supported chunk families include bKGD, cHRM, gAMA, hIST, iCCP, iTXt, oFFs, pCAL, sCAL, pHYs, sBIT, sPLT, sRGB, tEXt, tIME, tRNS, zTXt, unknown chunks, and user chunks.

`PNG_INFO_IMAGE_SUPPORTED` enables the `png_read_png()`/`png_write_png()` high-level helpers and `row_pointers` member in `png_info`.

## Public Typedefs

The file defines libpng’s base integer and pointer types:

- `png_uint_32` as `unsigned long`
- `png_int_32` as `long`
- `png_uint_16` as `unsigned short`
- `png_int_16` as `short`
- `png_byte` as `unsigned char`
- `png_size_t` as either configured `PNG_SIZE_T` or `size_t`
- `png_fixed_point` as `png_int_32`

It also defines `png_voidp`, byte/int/string pointer aliases, double pointer aliases, and `png_FILE_p` as `FILE *` or Windows CE `HANDLE`.

These typedefs are consumed throughout `png.h` and all implementation files.

## Export And Calling Convention Logic

The header defines `PNGAPI`, `PNG_IMPEXP`, `PNG_EXPORT`, and `PNG_EXPORT_VAR` across static, DLL, Windows, Cygwin, Borland/Microsoft, MinGW, and symbol-generation builds.

For ordinary non-Windows/non-DLL builds, `PNGAPI` and `PNG_IMPEXP` collapse to empty macros, so exported prototypes become normal C declarations.

The file also chooses between `PNG_USE_GLOBAL_ARRAYS` and `PNG_USE_LOCAL_ARRAYS`, with special behavior for Cygwin and DLL builds.

## Error And Memory Macros

`PNG_ABORT()` defaults to `abort()`.

If setjmp is supported, `png_jmpbuf(png_ptr)` maps to `png_ptr->jmpbuf`; otherwise it expands to an intentional compile-time failure marker.

The file abstracts string and memory operations through `png_strcpy`, `png_strncpy`, `png_strlen`, `png_memcmp`, `png_memcpy`, and `png_memset`. In normal builds these map to standard C functions; in far-memory builds they map to `_f*` variants.

It also defines `FAR`, `FARDATA`, and far pointer conversion macros for legacy segmented memory models.

## Internal/Assembler Configuration

Under `PNG_INTERNAL`, the file defines tunables for dithering and gamma:

- `PNG_DITHER_RED_BITS`, `PNG_DITHER_GREEN_BITS`, `PNG_DITHER_BLUE_BITS` default to `5`.
- `PNG_MAX_GAMMA_8` defaults to `11`.
- `PNG_GAMMA_THRESHOLD` defaults to `0.05`.

Read-side assembler support is enabled by default unless disabled. MMX code is enabled by default when assembler code is enabled. Default MMX thresholds are:

- `PNG_MMX_ROWBYTES_THRESHOLD_DEFAULT 128`
- `PNG_MMX_BITDEPTH_THRESHOLD_DEFAULT 9`

Actual assembler routines require build-specific defines such as `PNG_USE_PNGVCRD` or `PNG_USE_PNGGCCRD`.

## Research Notes

This file is the reason `png.h` has such a large conditional API and ABI surface. For any build/debugging work in this subtree, check `pngconf.h` and compile flags before assuming a symbol, structure field, or chunk handler exists.

For filesystem subset research, this is vendored codec configuration only. Its risk profile is portability and ABI drift, not filesystem semantics.
