# File Research: sources/os/plan9/9front/sys/src/cmd/gs/zlib/zutil.c

Implements target-dependent utility functions for the bundled zlib library.

Key points:
- Defines `z_errmsg[]`, indexed through `ERR_MSG`, for zlib return-code strings.
- `zlibVersion()` returns `ZLIB_VERSION`.
- `zlibCompileFlags()` encodes compile-time size, compiler, assembler, debug, table-generation, missing-feature, and sprintf/snprintf options into a bitfield.
- Under `DEBUG`, provides `z_verbose` and fatal `z_error()`.
- `zError()` exposes error-code-to-string conversion.
- Provides fallback `zmemcpy`, `zmemcmp`, and `zmemzero` when `HAVE_MEMCPY` is unavailable.
- Contains legacy 16-bit allocation implementations for Turbo C and Microsoft C.
- Default `zcalloc()`/`zcfree()` use `malloc` or `calloc` depending on `sizeof(uInt)` and call `free`.

Dependencies and interactions:
- Includes `zutil.h`.
- Supplies allocation and memory routines used by deflate/inflate internals.
- Error strings are used by `ERR_RETURN` and public `zError()`.

Research relevance:
- This is the portability and allocator layer for the vendored zlib copy. It preserves old platform compatibility even though the Plan 9 build path mainly uses the normal allocator branch.
