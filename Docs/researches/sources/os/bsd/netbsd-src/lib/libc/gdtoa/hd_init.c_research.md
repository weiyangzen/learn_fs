# File Research: sources/os/bsd/netbsd-src/lib/libc/gdtoa/hd_init.c

Purpose: Initializes the hexadecimal digit lookup table used by hex parsing.

Core behavior:
- `htinit()` fills `hexdig` entries for a digit sequence with a fixed increment.
- `hexdig_init_D2A()` initializes mappings for `0-9`, `A-F`, and `a-f`.
- Encodes hex digit values offset so zero/non-hex can be distinguished cheaply.

Dependencies:
- Includes `gdtoaimp.h`.
- Writes the global `hexdig[]` declared in `gdtoaimp.h`.
