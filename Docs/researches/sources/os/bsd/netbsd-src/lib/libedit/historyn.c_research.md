# File Research: sources/os/bsd/netbsd-src/lib/libedit/historyn.c

## Purpose
Build shim for the narrow-character history implementation.

## Main Behavior
The file includes `config.h`, defines `NARROWCHAR`, then includes `history.c`. This causes `history.c`'s macro layer to map `Char` to `char`, `TYPE(type)` to the unqualified type, and string helpers to normal byte-string functions.

## Dependencies
Depends entirely on `history.c` and its conditional `NARROWCHAR` support.

## Risks And Notes
This file intentionally has no independent logic. Any behavioral change in narrow history comes from the shared implementation in `history.c`.
