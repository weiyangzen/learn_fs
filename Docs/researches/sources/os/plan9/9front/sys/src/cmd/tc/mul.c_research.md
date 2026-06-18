# File Research: sources/os/plan9/9front/sys/src/cmd/tc/mul.c

Finds short shift/add/subtract sequences for multiplication by integer constants.

Key points:
- `mulcon0` normalizes negative constants, checks a small cache, searches an exception hint table, then tries bounded sequence generation.
- Encoded sequences use pairs such as shift letters (`a` plus amount) and add/subtract operators with operand-routing digits.
- `docode` validates and expands encoded hints into executable sequence codes while simulating register values.
- `gen1`, `gen2`, and `gen3` recursively search for sequences within `maxmulops`, tracking whether temporary values have been shifted or used.
- If the constant has trailing zero bits, the code can recursively generate a sequence for the odd factor and append a final shift.
- `hintab` contains hand-supplied sequences for constants that the bounded search misses; `hintabsize` exports its length.

Dependencies and interactions:
- `swt.c` consumes generated `Multab` entries in `mulcon`.
- Uses `Multab` and `Hintab` definitions from `gc.h`.

Research relevance:
- Implements a classic compiler strength-reduction path for constant multiplication on Thumb.
