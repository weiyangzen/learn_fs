# File Research: sources/os/plan9/9front/sys/src/cmd/gs/libpng/png.h

Primary libpng 1.2.8 public/internal API header vendored under the 9front Ghostscript `libpng` tree. It defines the PNG library version contract, public data structures, exported functions, constants, transformation flags, and private prototypes used when building libpng itself.

Key elements:
- Declares libpng version `1.2.8`, header version string, DLL number `13`, build status flags, and numeric version macro `PNG_LIBPNG_VER 10208`.
- Includes `zlib.h` for compression types and `pngconf.h` for platform configuration, feature switches, typedefs, linkage macros, and setjmp/stdio behavior.
- Defines libpng public data structures:
  - `png_color`, `png_color_16`, `png_color_8`
  - `png_sPLT_entry`, `png_sPLT_t`
  - `png_text`
  - `png_time`
  - `png_unknown_chunk`
  - `png_info`
  - `png_row_info`
  - `png_struct_def`
- `png_info` stores image metadata and ancillary chunk state, with many conditional fields controlled by `PNG_*_SUPPORTED` feature macros.
- `png_struct_def` stores active read/write state: error callbacks, I/O callbacks, zlib stream, dimensions, row buffers, chunk/CRC state, transform flags, gamma tables, progressive-read buffers, user chunk handlers, optional user memory callbacks, MMX/assembler thresholds, and user dimension limits.
- Defines PNG constants for color types, compression/filter/interlace methods, ancillary chunk units, sRGB intents, info-valid bit flags, transform masks, CRC actions, filter selection, MNG feature flags, unknown chunk policies, assembler/MMX flags, and internal mode/transform flags.
- Declares the main public lifecycle functions:
  - version/signature checks: `png_access_version_number`, `png_sig_cmp`, `png_check_sig`
  - allocation/init: `png_create_read_struct`, `png_create_write_struct`, `png_create_info_struct`, legacy `png_read_init_*`/`png_write_init_*`
  - read/write flow: `png_read_info`, `png_read_update_info`, `png_read_row(s)`, `png_read_image`, `png_read_end`, `png_write_info`, `png_write_row(s)`, `png_write_image`, `png_write_end`
  - teardown: `png_destroy_read_struct`, `png_destroy_write_struct`, `png_destroy_info_struct`
- Declares transform configuration APIs including expansion, palette-to-RGB, grayscale/RGB conversion, alpha/filler handling, byte swap, packing, interlace handling, background composition, dithering, gamma correction, filtering, compression parameters, and flush control.
- Declares callback override APIs for stdio I/O, custom read/write functions, error/warning handlers, row status callbacks, user memory allocation, user transforms, user chunks, and progressive reading.
- Declares `png_get_*`/`png_set_*` metadata accessors for IHDR, PLTE, bKGD, cHRM, gAMA, hIST, oFFs, pCAL, pHYs, sBIT, sRGB, iCCP, sPLT, text chunks, tIME, tRNS, sCAL, unknown chunks, row pointers, and convenience image fields.
- Under `PNG_INTERNAL`, declares private helpers for allocation, zlib allocation callbacks, default I/O callbacks, CRC handling, endian read/write helpers, chunk writers, row filtering, row transforms, chunk handlers, progressive reader internals, MNG intrapixel transforms, and assembler/MMX initialization.

Dependencies:
- Directly includes `zlib.h` unless `PNG_VERSION_INFO_ONLY` is defined.
- Directly includes `pngconf.h`.
- Relies on `pngconf.h` for `png_uint_32`, `png_size_t`, `png_byte`, `PNG_EXPORT`, `PNGAPI`, `PNGARG`, `PNG_SETJMP_SUPPORTED`, `PNG_FLOATING_POINT_SUPPORTED`, read/write feature macros, and platform calling conventions.
- Public declarations are implemented across the rest of libpng: `png.c`, `pngread.c`, `pngwrite.c`, `pngget.c`, `pngset.c`, `pngrio.c`, `pngwio.c`, `pngrutil.c`, `pngwutil.c`, `pngrtran.c`, `pngwtran.c`, `pngmem.c`, `pngerror.c`, and optional assembler sources.

Research notes:
- This old libpng header exposes the full `png_struct_def` and `png_info` layouts, so compile-time feature macros affect ABI size and binary compatibility. The comments repeatedly warn applications to prefer accessor functions over direct struct access.
- The header serves both applications and libpng internals. Public symbols use `PNG_EXPORT`, while private prototypes under `PNG_INTERNAL` use `PNG_EXTERN`.
- Many APIs are retained for legacy compatibility, including deprecated direct init macros and compatibility with libpng 1.0.x feature selection.
- The header supports both floating-point and fixed-point color/gamma APIs; fixed-point remains available unless explicitly disabled.
- Security/resource guardrails include `PNG_USER_WIDTH_MAX`, `PNG_USER_HEIGHT_MAX`, `png_set_user_limits`, bounded `PNG_UINT_31_MAX`, checked memcpy/memset declarations, and CRC policy controls.
- The bundled version predates modern libpng hardening and API opacity; consumers should treat it as a historical compatibility dependency rather than a current libpng API model.
