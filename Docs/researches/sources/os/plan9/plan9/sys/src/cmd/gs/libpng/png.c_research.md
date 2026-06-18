# File Research: sources/os/plan9/plan9/sys/src/cmd/gs/libpng/png.c

General-purpose libpng 1.2.8 core utility file.

Version and global data:

- Defines `PNG_INTERNAL` and includes `png.h`.
- Uses a typedef guard to force a compile-time mismatch if an older `png.h` is found.
- Under `PNG_USE_GLOBAL_ARRAYS`, defines the libpng version string, PNG signature bytes, chunk-name constants, and Adam7 interlace pass tables/masks.

Signature, zlib, and CRC helpers:

- `png_set_sig_bytes()` records how many PNG signature bytes the caller already consumed.
- `png_sig_cmp()` compares a caller-supplied byte range against the PNG signature.
- `png_check_sig()` is the obsolete boolean signature wrapper.
- `png_zalloc()` and `png_zfree()` provide zlib allocation/free hooks backed by libpng memory functions, with overflow checking.
- `png_reset_crc()` and `png_calculate_crc()` manage chunk CRC state while respecting configured CRC ignore/use flags.

`png_info` lifecycle:

- `png_create_info_struct()` allocates and initializes a public info struct.
- `png_destroy_info_struct()` destroys a single info struct.
- `png_info_init()` and `png_info_init_3()` zero/reinitialize info storage and handle older ABI size expectations.
- `png_data_freer()` sets ownership policy bits when `PNG_FREE_ME_SUPPORTED` is enabled.
- `png_free_data()` frees selected owned fields: text, transparency, sCAL, pCAL, iCCP, suggested palettes, unknown chunks, histogram, palette, and row pointers.
- `png_info_destroy()` frees all info-owned data, unknown chunk lists, and reinitializes the struct.

Other API helpers:

- `png_get_io_ptr()` returns the user I/O pointer.
- `png_init_io()` stores a `FILE *` as the default I/O pointer when stdio is available.
- `png_convert_to_rfc1123()` formats PNG time data as an RFC 1123-style UTC string.
- `png_get_copyright()`, `png_get_libpng_ver()`, `png_get_header_ver()`, `png_get_header_version()`, and `png_access_version_number()` expose version/copyright strings and numeric version.
- `png_handle_as_unknown()` queries caller-configured unknown-chunk handling.
- `png_reset_zstream()` calls zlib `inflateReset()`.
- `png_init_mmx_flags()` initializes assembler/MMX capability flags when compiled with assembler support; `png_mmx_support()` returns `-1` in builds without runtime MMX detection.
- `png_convert_size()` safely narrows `size_t` to `png_size_t` when `PNG_SIZE_T` is configured.

This is library support plumbing for libpng memory ownership, metadata cleanup, signatures, CRC, versioning, I/O pointer storage, and optional CPU feature flags.
