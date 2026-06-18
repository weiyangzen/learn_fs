# File Research: sources/os/plan9/9front/sys/src/cmd/bzip2/lib/bzzlib.c

Purpose: Implements zlib-style convenience functions on top of the higher-level bzip2 stdio API.

Key points:
- `bzopen_or_bzdopen` parses mode strings for read/write, block size digits, and small decompression mode.
- `BZ2_bzopen` opens by path or uses stdin/stdout when the path is empty or nil.
- `BZ2_bzdopen` wraps an existing file descriptor using `fdopen` unless strict ANSI disables it.
- `BZ2_bzread` returns byte count, 0 after stream end, or -1 on error.
- `BZ2_bzwrite` returns requested length on success or -1 on error.
- `BZ2_bzflush` is a no-op returning 0.
- `BZ2_bzclose` closes compression/decompression and then closes the underlying file except stdin/stdout.
- `BZ2_bzerror` maps last error codes to strings.

Dependencies and interactions:
- Built on `BZ2_bzReadOpen`, `BZ2_bzWriteOpen`, `BZ2_bzRead`, `BZ2_bzWrite`, and close functions.
- Uses `bzFile.lastErr` directly.
- Contains non-Plan-9 conditional binary-mode support for Windows-like targets.

Research notes:
- This is compatibility glue, explicitly marked as contributed zlib-compatibility code and not originally part of the core upstream library.
- `BZ2_bzerror` assumes non-null `b` and `errnum`; it is a thin compatibility layer rather than a defensive API.
