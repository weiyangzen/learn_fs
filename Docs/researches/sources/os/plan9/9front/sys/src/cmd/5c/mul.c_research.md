# File Research: sources/os/plan9/9front/sys/src/cmd/5c/mul.c

This file searches for short shift/add/sub instruction sequences to replace integer multiplication by constants.

Key behavior:
- Encodes multiply plans as compact two-character operation pairs:
  - letters `a`-... mean left shift by a count,
  - `+` and `-` mean add/sub combinations,
  - numeric suffix bits select source/destination temporary roles.
- `mulcon0(long v)` normalizes negative constants, checks a small cache, tries a sorted hint table, searches up to `maxmulops`, then tries factoring powers of two recursively.
- `docode()` validates and materializes a candidate hint/search sequence against the target multiplier.
- `gen1()`, `gen2()`, and `gen3()` recursively search possible shift/add/sub sequences under operation-count bounds.
- `hintab[]` contains exceptional constants whose sequences are known because the search misses them.
- `hintabsize` exposes the table size.

Dependencies and interactions:
- Consumed by `swt.c:mulcon()` and `cgen.c` multiplication paths.
- Uses `Multab` and `Hintab` from `gc.h`.

Research relevance:
- This is an old-school strength-reduction engine for ARM, where short shift/add/sub sequences can beat multiply.

Risk notes:
- Search is bounded and heuristic; `hintab` entries are required for known failures.
- The cache stores negative constants as positive absolute values, with sign handled later.
- The compact sequence language is non-obvious; changes need cross-checking against generated instructions.
