# File Research: sources/os/plan9/9front/sys/src/cmd/bzip2/lib/bzlib_stdio_private.h

Purpose: Private definitions for the stdio wrapper layer around libbzip2 streams.

Key points:
- Replaces silent internal assertion/logging macros from `bzlib_private.h` with stdio-aware versions.
- Defines `BZ_SETERR`, which writes errors both to the caller-provided `bzerror` pointer and to `bzFile.lastErr`.
- Defines concrete `bzFile` containing `FILE *handle`, a `BZ_MAX_UNUSED` buffer, writing/read mode, `bz_stream`, last error, and initialization status.
- Declares `bz_feof(FILE*)`.

Dependencies and interactions:
- Included by `bzread.c`, `bzwrite.c`, and `bzzlib.c`.
- Uses `FILE`, `fprintf`, and optionally `exit` for debug assertions.
- `bzstdio.c` supplies `bz_feof`.

Research notes:
- This header is the glue between the public opaque `BZFILE` handle and the underlying `bz_stream`.
- Error propagation is macro-based and assumes local variables named `bzerror` and `bzf`, so call sites must preserve that convention.
