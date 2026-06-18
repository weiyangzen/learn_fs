# File Research: sources/os/plan9/9front/sys/src/cmd/gs/libpng/png.c

General-purpose libpng 1.2.8 implementation file providing version data, signature helpers, zlib allocation hooks, CRC helpers, info-struct lifecycle, IO pointer setup, version/copyright accessors, unknown-chunk policy lookup, zstream reset, MMX flag initialization, and size conversion.

Version and constants:
- Declares compile-time guard `typedef version_1_2_8 Your_png_h_is_not_version_1_2_8`.
- Under `PNG_USE_GLOBAL_ARRAYS`, defines `png_libpng_ver`, PNG signature bytes, chunk-name constants, and Adam7 pass arrays/masks.
- `png_get_copyright`, `png_get_libpng_ver`, `png_get_header_ver`, `png_get_header_version`, and `png_access_version_number` expose version metadata.

Signature and zlib support:
- `png_set_sig_bytes` records how many PNG signature bytes the caller already consumed, rejecting values above 8.
- `png_sig_cmp` compares partial or full signatures against the PNG magic bytes; `png_check_sig` is the obsolete wrapper.
- `png_zalloc` checks multiplication overflow before allocating zlib memory through libpng allocation and temporarily permits NULL returns.
- `png_zfree` delegates zlib frees to `png_free`.

CRC and info lifecycle:
- `png_reset_crc` initializes CRC state with zlib `crc32`.
- `png_calculate_crc` updates CRC unless flags say the current critical/ancillary CRC can be ignored.
- `png_create_info_struct`, `png_destroy_info_struct`, `png_info_init`, and `png_info_init_3` allocate, destroy, and initialize `png_info`.
- `png_data_freer`, `png_free_data`, and `png_info_destroy` manage ownership/freeing for text, transparency, sCAL, pCAL, iCCP, sPLT, unknown chunks, hIST, PLTE, and row pointers.

IO and utility functions:
- `png_get_io_ptr` returns the application IO pointer.
- `png_init_io` stores a stdio `FILE *` when stdio support is enabled.
- `png_convert_to_rfc1123` formats PNG time into RFC 1123-style text.
- `png_handle_as_unknown` returns per-chunk unknown-handling policy.
- `png_reset_zstream` calls `inflateReset`.
- `png_init_mmx_flags` initializes assembler/MMX flags and thresholds when compiled with assembler support; fallback `png_mmx_support` returns `-1`.
- `png_convert_size` aborts if a platform `size_t` cannot fit in `png_size_t`.

Filesystem relevance:
- Core image library support code. It exposes stdio pointer initialization but contains no filesystem implementation logic.
