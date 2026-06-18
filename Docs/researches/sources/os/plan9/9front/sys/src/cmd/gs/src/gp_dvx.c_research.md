# File Research: sources/os/plan9/9front/sys/src/cmd/gs/src/gp_dvx.c

DesqView/X-specific Ghostscript platform routines.

Key behavior:
- Provides no-op init/exit and `exit`-based termination.
- Uses `strerror` for OS error strings.
- Implements realtime through `gettimeofday`, with user time as realtime approximation.
- Stubs persistent cache insert/query.
- Opens the default printer as `stdprn`/`PRN` or a named file, setting binary mode when needed.
- Stubs native font enumeration.

Notable dependencies:
- Uses common MS-DOS printer binary-mode helper `gp_set_file_binary`.
- Includes `time_.h`, `gsexit.h`, and `gp.h`.

Research notes:
- Cache functions are marked “not yet implemented” but return success for insert and failure for query.
