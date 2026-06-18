# File Research: sources/os/bsd/dragonflybsd/sys/vfs/hammer2/zlib/hammer2_zlib_zutil.c

Source read: complete file, 182 lines.

Purpose: Target-dependent zlib utility implementation. It provides version/error strings, compile-flag introspection, debug panic/error handling, and fallback memory routines when libc-style memory functions are unavailable.

Key interfaces:
- `zlibVersion()` returns `ZLIB_VERSION`.
- `zlibCompileFlags()` encodes type sizes and compile-time feature flags such as debug, assembly, dynamic CRC, gzip support, PKZIP workaround, and formatting behavior.
- `zError(int err)` maps zlib error codes through `z_errmsg`.
- Under `H2_ZLIB_DEBUG`, `z_error()` panics in kernel builds or prints/exits outside the kernel.
- If `HAVE_MEMCPY` is not defined, `zmemcpy()`, `zmemcmp()`, and `zmemzero()` are supplied.

Integration:
- Included by internal zlib code through `hammer2_zlib_zutil.h`.
- Uses `Z_PREFIX` mapping from `hammer2_zlib_zconf.h`, so visible names are prefixed in normal builds.

Risks and review notes:
- `zError()` indexes `z_errmsg` through `ERR_MSG(err)` and assumes valid zlib error-code ranges.
- Debug panic behavior is appropriate for invariant failures but too aggressive for malformed input paths; callers should not route normal data errors through `Assert`.
