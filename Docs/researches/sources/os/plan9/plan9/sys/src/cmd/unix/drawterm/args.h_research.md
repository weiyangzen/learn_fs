# File Research: sources/os/plan9/plan9/sys/src/cmd/unix/drawterm/args.h

Read fully: 20 lines, 709 bytes. SHA-256 prefix: `8d3fa47b883657cc`.

This header provides Plan 9-style argument parsing macros for drawterm.

It defines:
- external `argv0`
- `ARGBEGIN` / `ARGEND`
- `ARGF()` for optional attached/next-argument option values
- `EARGF(x)` for required option values with fallback expression
- `ARGC()` for the current rune option character

Integration: used by `cpu.c` and `cpu-bl.c` to parse drawterm command-line options while preserving Plan 9 coding style.

Risk notes: these macros mutate `argc`/`argv` and local hidden variables, so they depend on conventional usage shape.
