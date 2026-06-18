# File Research: sources/os/plan9/9front/sys/src/cmd/qc/mul.c

Constant-multiply sequence generator. It replaces multiplication by constants with shifts/adds/subtracts when a short sequence is available.

Key responsibilities:
- `mulcon0` looks up cached multiply sequences, checks exception hints, searches for shift/add/sub recipes, and handles powers of two recursively.
- `docode` validates compact hint strings against a target constant.
- `gen1`, `gen2`, and `gen3` search candidate operation sequences.
- `hintab` stores constants that the search algorithm fails to find efficiently.
- `hintabsize` exposes the hint table size.

Dependencies and coupling:
- Used by `swt.c:mulcon`, which translates compact sequence strings into generated instructions.
- Uses `Multab`/`Hintab` from `gc.h`.

Notable behavior:
- The compact code language encodes shift counts as letters and add/sub operand routing as digits.
- Negative constants are normalized during sequence lookup, then negated in emission.
