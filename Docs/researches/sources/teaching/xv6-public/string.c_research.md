# File Research: sources/teaching/xv6-public/string.c

Kernel string and memory routines.

Implements:
- `memset`, optimized to use `stosl` on 4-byte aligned/length cases.
- `memcmp`.
- Overlap-safe `memmove`.
- `memcpy` as a wrapper around `memmove`.
- `strncmp`.
- `strncpy`.
- `safestrcpy`, guaranteed to NUL-terminate when size > 0.
- `strlen`.

Used throughout kernel code instead of libc.
