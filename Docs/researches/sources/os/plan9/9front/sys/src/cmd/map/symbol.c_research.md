# File Research: sources/os/plan9/9front/sys/src/cmd/map/symbol.c

Parses and draws named vector symbols for the `map -y` option.

Key behavior:
- Reads a symbol file containing range commands, symbol starts, move commands, and vertex records.
- Stores up to `NSYMBOL` named symbol paths as arrays of `symb` points with segment/end flags.
- Scales symbol coordinates relative to global `halfwidth` and the last parsed range.
- `putsym()` finds a named symbol, projects the geographic position, computes local rotation/upright orientation, and plots the vector points with `cpoint`.
- Supports upright, normal, and reverse rotation modes.

Important dependencies: `map.h`, `iplot.h`, global `halfwidth`, `vflag`, `projection`, `doproj`, and `cpoint`.

Notable risks:
- Symbol names are limited to 10 bytes and the symbol table is fixed at 20 entries.
- Parser is minimal; malformed files call `error()` or can leave empty symbols.
