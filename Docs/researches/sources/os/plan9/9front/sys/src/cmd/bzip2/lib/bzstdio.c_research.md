# File Research: sources/os/plan9/9front/sys/src/cmd/bzip2/lib/bzstdio.c

Purpose: Provides a portable EOF probe helper for the bzip2 stdio wrapper.

Key points:
- Defines `bz_feof(FILE *f)`.
- Reads one byte with `fgetc`.
- Returns true if EOF is reached.
- Otherwise pushes the byte back with `ungetc` and returns false.

Dependencies and interactions:
- Used by `bzread.c` to distinguish no buffered input from real file EOF.
- Includes `os.h`, `bzlib.h`, and `bzlib_private.h`.

Research notes:
- The helper deliberately avoids relying only on stdio EOF flags, which may not be set until a read has been attempted.
