# File Research: sources/os/plan9/9front/sys/src/cmd/upas/fs/extra/prflags.c

This helper prints decoded flag strings from index-like input.

Key behavior:
- Reads stdin line by line.
- Tokenizes each line into `Fields` fields.
- Skips records with first field `-`.
- Parses field 1 as hex flags and prints the fixed-width `flagbuf` representation.

Integration and risks:
- Depends on `common.h` flag constants and `Fields`.
