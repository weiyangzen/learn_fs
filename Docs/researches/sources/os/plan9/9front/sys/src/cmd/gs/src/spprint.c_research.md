# File Research: sources/os/plan9/9front/sys/src/cmd/gs/src/spprint.c

Implements lightweight ASCII value printing on Ghostscript streams.

Key points:
- `stream_write` and `stream_puts` write byte arrays and C strings to streams.
- `pprintf_scan` copies literal format text up to the next non-escaped `%`.
- Provides fixed-arity integer printers `pprintd1..4`, long printers `pprintld1..3`, string printers `pprints1..3`, and float printers `pprintg1..6`.
- Float printing uses `%g` but falls back to `%f` formats if exponential notation appears, because PDF disallows `%e`-style numeric syntax.
- Fixed-arity functions avoid portability problems with variadic functions on older compilers.

Dependencies and interactions:
- Used by PostScript/PDF output code, including parameter printing in `spsdf.c`.

Research relevance:
- Portable stream-oriented formatting helpers for generated PostScript/PDF syntax.
