# File Research: sources/os/plan9/plan9/sys/src/cmd/bzip2/lib/bzlib_stdio_private.h

Private header for the stdio wrapper layer. It overrides the no-op/private-header assertion and verbose-print macros so stdio code can report diagnostics through `stderr` and `BZ2_bz__AssertH__fail`.

It defines `BZ_SETERR`, which updates both the caller’s `bzerror` pointer and the `bzFile.lastErr` field when available. The internal `bzFile` struct stores the underlying `FILE*`, an unused/input-output staging buffer, mode flag, embedded `bz_stream`, last error, and initialization flag.

The only external helper declared here is `bz_feof(FILE*)`, implemented in `bzstdio.c`. This header is consumed by `bzread.c`, `bzwrite.c`, and `bzzlib.c`.
