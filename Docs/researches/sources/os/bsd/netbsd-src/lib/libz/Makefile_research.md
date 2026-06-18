# File Research: sources/os/bsd/netbsd-src/lib/libz/Makefile

## Summary
Builds NetBSD’s zlib library from the common imported zlib source directory.

## Main Responsibilities
- Sets warning level and enables `_FORTIFY_SOURCE` by default through `USE_FORT`.
- Uses `${NETBSDSRCDIR}/common/dist/zlib` as `ZLIBDIR`.
- Builds core zlib and gzip stream sources into `LIB=z`.
- Installs `zconf.h`, `zlib.h`, and `zlib.pc`.
- Adds `-DZLIB_CONST` and zlib include path.
- Suppresses implicit-fallthrough warnings for selected inflate sources.
- Defines a `test` target that builds and round-trips `minigzip`.

## Risks
The `minigzip` target intentionally omits normal `CFLAGS` to check standalone header usability. Library behavior follows vendored zlib sources outside this file.
