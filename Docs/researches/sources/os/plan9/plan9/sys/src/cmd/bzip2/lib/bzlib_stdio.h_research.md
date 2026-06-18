# File Research: sources/os/plan9/plan9/sys/src/cmd/bzip2/lib/bzlib_stdio.h

Public stdio-oriented bzip2 API declarations for the split Plan 9 libbzip2 copy. It defines `BZ_MAX_UNUSED`, aliases `BZFILE` to an opaque `void`, and declares zlib-like high-level file APIs.

The API surface includes `BZ2_bzopen`, `BZ2_bzdopen`, `BZ2_bzread`, `BZ2_bzwrite`, `BZ2_bzflush`, `BZ2_bzclose`, and `BZ2_bzerror`, plus the lower-level `BZ2_bzReadOpen/Read/ReadClose/ReadGetUnused` and `BZ2_bzWriteOpen/Write/WriteClose/WriteClose64`.

It depends on `FILE` from stdio and on the public `BZ_EXTERN`/`BZ_API` macros from `bzlib.h`. The comments preserve upstream bzip2 changelog notes around zero-length flush/read behavior and parameter fixes.
