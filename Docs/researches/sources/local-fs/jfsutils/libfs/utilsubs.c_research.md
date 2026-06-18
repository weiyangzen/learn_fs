# File Research: sources/local-fs/jfsutils/libfs/utilsubs.c

This file provides small shared utility functions.

Functions:
- `log2shift(uint32_t n)` returns the base-2 shift for powers of two, or `-1` if `n` is not a power of two.
- `prompt(char *str)` prints a prompt, reads up to 80 bytes from stdin, and returns the first input character.
- `more()` prints a pager-style prompt and returns 1 only when the user enters `x`; otherwise it returns 0 to continue.

Integration points:
- Declared in `utilsubs.h`.
- Used across command-line jfsutils code for sizing and simple interactive prompts.

Risks and notes:
- `prompt()` and `more()` do not handle `fgets()` returning `NULL`; they may return stale/uninitialized stack data on EOF or read error.
- `log2shift(0)` returns 0 because the loop does not execute, even though zero is not a power of two.
