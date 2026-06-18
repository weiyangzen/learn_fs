# File Research: sources/os/plan9/9front/sys/src/cmd/bzip2/lib/bzlib_stdio.h

Purpose: Public stdio-oriented bzip2 API declarations for the split 9front bzip2 library.

Key points:
- Includes `<stdio.h>` and defines `BZ_MAX_UNUSED` as 5000.
- Uses opaque `typedef void BZFILE`.
- Declares zlib-like APIs: `BZ2_bzopen`, `BZ2_bzdopen`, `BZ2_bzread`, `BZ2_bzwrite`, `BZ2_bzflush`, `BZ2_bzclose`, and `BZ2_bzerror`.
- Declares higher-level stdio APIs: `BZ2_bzReadOpen`, `BZ2_bzRead`, `BZ2_bzReadGetUnused`, `BZ2_bzReadClose`, `BZ2_bzWriteOpen`, `BZ2_bzWrite`, `BZ2_bzWriteClose`, and `BZ2_bzWriteClose64`.

Dependencies and interactions:
- Consumed by `bzread.c`, `bzwrite.c`, and `bzzlib.c`.
- Relies on `BZ_EXTERN` and `BZ_API` macros from the public bzip2 header.
- The concrete `BZFILE` implementation is private in `bzlib_stdio_private.h`.

Research notes:
- This file is API surface, not implementation. It preserves upstream bzip2 compatibility while allowing the Plan 9 tree to compile the stdio wrapper separately.
