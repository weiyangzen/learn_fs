# File Research: sources/os/plan9/9front/sys/src/cmd/bzip2/lib/bzfeof.c

This is a tiny stdio helper for libbzip2’s stdio layer.

Behavior:
- `bz_feof(FILE *f)` reads one byte with `fgetc`.
- If EOF, returns true.
- Otherwise pushes the byte back with `ungetc` and returns false.

Notable implementation details:
- It checks practical EOF state without consuming data.
- Uses libbzip2 `Bool` type and stdio headers.
