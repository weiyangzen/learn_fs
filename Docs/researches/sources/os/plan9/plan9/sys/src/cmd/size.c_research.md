# File Research: sources/os/plan9/plan9/sys/src/cmd/size.c

Plan 9 executable size reporter.

Key behavior:
- Opens each supplied file and parses an executable header with `crackhdr()`.
- Prints text, data, bss, total, and filename.
- Defaults to `8.out` when no arguments are provided.
- Reports non-a.out inputs as errors.

Important details:
- Uses libmach `Fhdr`.
- Exits with `"error"` if any input fails.

Filesystem relevance:
- Direct read-only inspection of executable files.
