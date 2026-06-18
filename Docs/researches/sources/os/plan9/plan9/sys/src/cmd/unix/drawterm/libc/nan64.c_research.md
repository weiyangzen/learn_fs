# File Research: sources/os/plan9/plan9/sys/src/cmd/unix/drawterm/libc/nan64.c

This file implements NaN and infinity helpers for 64-bit doubles.

Key behavior:
- `__NaN` constructs a quiet NaN.
- `__Inf` constructs signed infinity.
- `__isNaN` and `__isInf` inspect double bit patterns.

Important details:
- Handles endian/word-order differences with conditional layout logic.
- Used by float parsing/formatting.
