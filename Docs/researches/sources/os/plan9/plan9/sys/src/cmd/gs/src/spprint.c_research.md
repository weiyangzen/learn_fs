# File Research: sources/os/plan9/plan9/sys/src/cmd/gs/src/spprint.c

Small formatted-printing utilities for writing ASCII values to Ghostscript streams.

Key behavior:
- `stream_write` and `stream_puts` write byte arrays and C strings to a stream.
- `pprintf_scan` writes literal format text through the next substitution marker, treating `%%` as a literal `%`.
- `pprintd*`, `pprintld*`, `pprintg*`, and `pprints*` provide fixed-arity substitutions for ints, longs, floats, and strings.
- Floating-point printing uses `%g`, but if exponential notation appears it retries with fixed formatting because PDF disallows exponent notation in this context.

Notable dependencies:
- `stream.h` output APIs.
- `math_.h` for `fabs`.

Research notes:
- These helpers exist because older C varargs support was inconsistent across target compilers.
- Format validation is debug-only and assumes callers pass matching fixed-arity formats.
