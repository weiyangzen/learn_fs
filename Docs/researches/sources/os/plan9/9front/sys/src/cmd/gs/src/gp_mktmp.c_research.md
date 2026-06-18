# File Research: sources/os/plan9/9front/sys/src/cmd/gs/src/gp_mktmp.c

Replacement `mktemp` implementation for platforms lacking one.

Key behavior:
- Requires a filename ending in `XXXXXX`.
- Replaces the suffix with `AA.AAA`.
- Uses `stat` to test for existing files.
- Increments alphabetic characters, skipping dots, until an unused name is found or the space is exhausted.

Research notes:
- This only generates a candidate name; it does not atomically create the file, so callers must open carefully.
