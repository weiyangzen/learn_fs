# File Research: sources/os/bsd/dragonflybsd/sys/vfs/hammer2/zlib/hammer2_zlib_zutil.h

Source read: complete file, 149 lines.

Purpose: Internal zlib utility header. It defines local/internal linkage macros, common zlib constants, utility typedefs, error-return helpers, memory function selection, debug tracing macros, and byte-swap support.

Key definitions:
- `ZLIB_INTERNAL` optionally sets hidden visibility.
- `local` defaults to `static`.
- `uch`, `ush`, and `ulg` abbreviate unsigned byte/short/long types.
- `ERR_MSG()` and `ERR_RETURN()` centralize stream error reporting.
- Deflate block type constants `STORED_BLOCK`, `STATIC_TREES`, and `DYN_TREES`.
- Match constants `MIN_MATCH` and `MAX_MATCH`, dictionary flag `PRESET_DICT`, defaults for window and memory level, and `ZSWAP32()`.
- `Assert` and trace macros compile away unless `H2_ZLIB_DEBUG` is set.

Integration:
- Includes `<sys/param.h>` for `panic()` and `hammer2_zlib.h` for the public zlib API.
- Used throughout the HAMMER2 zlib source set.

Risks and review notes:
- Memory routine macros map to `memcpy`, `memcmp`, and `memset` when `HAVE_MEMCPY` is detected; kernel availability and include ordering should remain verified.
- Debug tracing references stdio only in debug builds, which may not be suitable for kernel configurations unless guarded consistently.
