# File Research: sources/os/plan9/plan9/sys/src/cmd/gs/zlib/zutil.h

Internal zlib configuration and utility header.

- Marks `ZLIB_INTERNAL` and includes the public `zlib.h`.
- Defines internal aliases `uch`, `ush`, `ulg`, `local`, error-message macros, block-type constants, match-length constants, and preset-dictionary flag.
- Selects `OS_CODE`, `F_OPEN`, `fdopen`, and platform includes for many historical targets.
- Defines availability or replacements for `vsnprintf`, `strerror`, `memcpy`, `memcmp`, and `memset`.
- Defines debug tracing/assertion macros and no-op versions for non-debug builds.
- Declares `zcalloc()` and `zcfree()` and wraps them through `ZALLOC`, `ZFREE`, and `TRY_FREE`.

Dependencies are `zlib.h`, standard C headers when `STDC` is enabled, and many compile-time platform defines. Applications should not include it directly; it is for zlib internals.

Notable concerns: platform detection defaults unknown targets to Unix `OS_CODE 0x03`, which is likely how this Plan 9 copy behaves unless build flags override it.
