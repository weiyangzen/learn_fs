# File Research: sources/os/plan9/9front/sys/src/cmd/gs/libpng/pngconf.h

Machine and build configuration header for libpng 1.2.8. It selects supported libpng features, includes platform headers, defines core libpng scalar/pointer types, and normalizes export/calling-convention macros across C, Windows, Cygwin, OS/2, DOS memory models, and normal Unix-like builds.

Key elements:
- Defines `PNG_1_2_X`.
- Optionally includes `pngusr.h` when `PNG_USER_CONFIG` is supplied.
- Documents private DLL metadata macros such as `PNG_USER_PRIVATEBUILD`, `PNG_USER_DLLFNAME_POSTFIX`, and version-info strings.
- Sets default compression buffer size `PNG_ZBUF_SIZE 8192`.
- Enables read and write support by default unless `PNG_NO_READ_SUPPORTED` or `PNG_NO_WRITE_SUPPORTED` is defined.
- Enables MNG features, floating-point support, fixed-point support, free-me ownership tracking, easy accessors, user memory callbacks, user limits, error numbers, and most read/write transforms by default unless explicitly disabled.
- Handles platform headers and feature availability:
  - includes `stdio.h` unless `PNG_NO_STDIO` or Windows CE restrictions apply
  - includes `setjmp.h` when `PNG_SETJMP_SUPPORTED`
  - includes `string.h` or `strings.h`
  - includes `math.h`/Mac `fp.h` under internal floating-point builds
  - includes `time.h` when tIME support requires it
  - includes memory/model headers for older DOS/Windows compilers
- Defines feature-selection cascades for:
  - read transforms: expand, shift, pack, BGR, swap, packswap, invert, dither, background, 16-to-8, filler, gamma, gray-to-RGB, alpha operations, user transform, RGB-to-gray
  - write transforms: shift, pack, BGR, swap, packswap, invert, filler, alpha operations, user transform
  - progressive read and read/write interlacing
  - ancillary chunks: bKGD, cHRM, gAMA, hIST, iCCP, iTXt, oFFs, pCAL, pHYs, sBIT, sCAL, sPLT, sRGB, tEXt, tIME, tRNS, zTXt, unknown chunks, user chunks
- Defines `PNG_LEGACY_SUPPORTED` behavior that disables newer fields/features to preserve older structure sizes.
- Defines core libpng types:
  - `png_uint_32`, `png_int_32`, `png_uint_16`, `png_int_16`, `png_byte`
  - `png_size_t`
  - pointer typedefs such as `png_voidp`, `png_bytep`, `png_charp`, `png_const_charp`, `png_doublep`, pointer-to-pointer variants, and zlib aliases
  - `png_fixed_point`
  - `png_FILE_p`
- Defines `FAR`, `FARDATA`, and far/near memory helper macros for old segmented-memory compilers.
- Configures DLL/static linkage and symbol export macros:
  - `PNG_DLL`, `PNG_BUILD_DLL`, `PNG_USE_DLL`, `PNG_STATIC`
  - `PNGAPI`
  - `PNG_IMPEXP`
  - `PNG_EXPORT`
  - `PNG_EXPORT_VAR`
- Defines `png_jmpbuf`, `PNG_ABORT`, string/memory wrapper macros (`png_memcpy`, `png_strncpy`, etc.), and MMX threshold defaults for internal read builds.
- Caps `PNG_ZBUF_SIZE` at 64 KiB when `PNG_MAX_MALLOC_64K` is active.

Dependencies:
- May include user configuration file `pngusr.h`.
- Supplies definitions consumed by `png.h` and every libpng source file.
- Depends on standard headers according to feature/platform switches: `stdio.h`, `setjmp.h`, `string.h`/`strings.h`, `stdlib.h`, `math.h`, `time.h`, and platform-specific Windows/DOS/Mac headers.
- Depends on zlib typedefs already visible through `zlib.h` before the zlib alias typedef section.

Research notes:
- This file is the central compile-time ABI switchboard. Changing feature macros can add/remove fields from `png_info` and `png_struct_def`, which is unsafe for shared-library compatibility with applications compiled against different settings.
- The default configuration is broad: read/write support, transforms, ancillary chunks, progressive read, unknown chunks, user memory, and user limits are mostly enabled.
- `PNG_NO_STDIO` disables more than console messages; it also affects default file I/O APIs and some time/scale support paths.
- The Windows/Cygwin export handling is historical and complex, reflecting libpng’s cross-platform DLL/static build constraints in the 1.2 era.
- Plan 9/9front-specific logic is not present; this vendored header relies on the surrounding Ghostscript/libpng build to supply compatible C library and zlib behavior.
