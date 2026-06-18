# File Research: sources/os/bsd/netbsd-src/lib/libc/gdtoa/smisc.c

Purpose: Shared parser-side `Bigint` utilities.

Core behavior:
- `s2b()` converts decimal digits from a source string into a `Bigint`.
- `ratio()` computes an approximate floating ratio of two `Bigint`s.
- `match()` case-insensitively matches `inf`/`nan` suffixes when infinity/NaN parsing is enabled.
- `copybits()` copies a `Bigint` into a fixed-width word array.
- `any_on()` checks whether any discarded low bits are nonzero.

Dependencies:
- Includes `gdtoaimp.h`.
- Uses `Balloc`, `multadd`, `b2d`, `lo0bits`, `Storeinc`, and bit packing macros.
