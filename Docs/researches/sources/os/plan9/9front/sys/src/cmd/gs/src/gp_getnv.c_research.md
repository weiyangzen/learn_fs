# File Research: sources/os/plan9/9front/sys/src/cmd/gs/src/gp_getnv.c

Standard `gp_getenv` implementation.

Key behavior:
- Wraps the C library `getenv`.
- Copies the environment value into the supplied buffer when it fits.
- Returns `0` on success, `-1` when the buffer is too small, and `1` when the key is missing.
- Always updates `*plen` to the required length including the null terminator.

Research notes:
- Missing variables produce an empty string if the caller supplied a nonzero buffer length.
