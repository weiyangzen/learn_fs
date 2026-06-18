# File Research: sources/os/plan9/9front/sys/src/cmd/gs/src/md5main.c

## Purpose
Standalone command-line utility for the MD5 package.

## Main Structure
- Supports `--test`, `--t-values`, and `--version`.
- `do_test` runs seven RFC 1321 test vectors and compares hex digests.
- `do_t_values` prints generated `T1` through `T64` constants from `floor(2^32 * abs(sin(i)))`.
- `main` dispatches on one argument or prints usage.

## Integration Notes
- Intended compilation example: `gcc -o md5main -lm md5main.c md5.c`.
- Not part of the Ghostscript runtime library path unless explicitly built as a utility.

## Risks and Edge Cases
- Returns `0` after usage text for invalid arguments, so misuse is not signaled as command failure.
- Uses `sprintf` into a fixed correctly sized hex buffer for known 16-byte digest output.
