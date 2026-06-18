# File Research: sources/os/plan9/plan9/sys/src/cmd/map/symbol.c

Loads and draws user-defined map symbols for the `map -y` option.

Key data:
- `struct symb` stores symbol point coordinates, name, and segment/end flags.
- Up to `NSYMBOL` symbol definitions are stored in `symbol[]`.
- `halfrange` controls scaling from symbol source coordinates to plot space.

Key functions:
- `getsyms()` opens and reads a symbol file.
- `getsymbol()` parses symbol definitions, ranges, moves, and vertices.
- `getrange()` parses range commands.
- `putsym()` projects anchor point, computes symbol rotation, and draws symbol vectors using `cpoint()`.
- `setrot()` aligns symbols upright, normal, or reversed relative to projected local north.
- `dorot()` applies the 2x2 rotation/scale matrix.

Dependencies:
- Calls `doproj`, `cpoint`, `projection`, and `hypot`.
- Uses `iplot` drawing through map’s renderer callbacks.
