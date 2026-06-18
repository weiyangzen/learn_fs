# File Research: sources/local-fs/erofs-utils/fsck/Makefile.am

## Purpose
Automake build file for the `fsck.erofs` executable and optional libFuzzer target.

## Key Details
- Builds `bin_PROGRAMS = fsck.erofs` from `main.c`.
- Uses `-Wall -I$(top_srcdir)/include` and links `$(top_builddir)/lib/liberofs.la`.
- Adds `${libuuid_CFLAGS}` to preprocessor flags.
- Under `ENABLE_FUZZING`, builds `fuzz_erofsfsck` from the same `main.c` with `-DFUZZING`.
- Fuzzer target links with `-fsanitize=address,fuzzer`.

## Interactions
- Depends on `lib/liberofs.la`, which supplies EROFS image parsing, decompression, xattrs, directory iteration, blob devices, and packed-file helpers.
- The fuzz target activates the alternate entry points in `fsck/main.c`.

## Notes
This file is build orchestration only; no runtime logic.
