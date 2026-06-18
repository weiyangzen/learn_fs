# File Research: sources/os/plan9/plan9/sys/src/cmd/gs/zlib/zutil.c

Target-dependent zlib utility implementation.

- Defines `z_errmsg[]`, mapping zlib status codes to messages through `ERR_MSG`.
- Implements `zlibVersion()` and `zlibCompileFlags()`.
- Provides debug-only `z_error()` and `z_verbose`.
- Exports `zError()` for converting zlib return codes to strings.
- Provides fallback `zmemcpy`, `zmemcmp`, and `zmemzero` when `HAVE_MEMCPY` is unavailable.
- Provides `zcalloc()` and `zcfree()` default allocation hooks, with special branches for legacy 16-bit Turbo C and Microsoft C models.

Dependencies are `zutil.h`, libc allocation, optional stdio for debug, and platform macros. In normal Plan 9/Ghostscript builds, the generic allocator path is the relevant one.

Notable concerns: the generic `zcalloc()` uses `malloc(items * size)` on systems with `sizeof(uInt) > 2` without overflow checking, matching old upstream zlib behavior. The many 16-bit branches are portability baggage rather than active Plan 9 behavior.
