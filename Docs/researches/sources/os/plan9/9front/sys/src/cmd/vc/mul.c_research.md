# File Research: sources/os/plan9/9front/sys/src/cmd/vc/mul.c

Purpose: Builds shift/add/sub instruction sequences for multiplication by integer constants.

Key behavior:
- `mulcon0` looks up or computes a compact code sequence for multiplying by a positive constant.
- Maintains a small cache in `multab`.
- Uses a sorted exception `hintab` for constants the search cannot find efficiently.
- Searches sequences up to bounded lengths using `gen1`, `gen2`, and `gen3`.
- `docode` verifies/generated encoded sequences by simulating register values.
- Supports recursive decomposition by factoring powers of two.

Dependencies:
- Uses `Multab` and `Hintab` from `gc.h`; consumed by `mulcon` in `swt.c`.

Notable details:
- The code sequence language encodes shifts as letters and arithmetic as `+`/`-` with operand-selector digits.
