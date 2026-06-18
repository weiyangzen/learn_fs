# File Research: sources/os/plan9/9front/sys/src/cmd/9c/mul.c

Constant-multiplication recipe search for the PowerPC64 compiler backend.

Key functions:
- `mulcon0` normalizes constants, checks a small cache, consults an exception hint table, searches shift/add/sub recipes up to a bounded length, and handles trailing power-of-two factors recursively.
- `docode` interprets recipe strings into concrete virtual-register operations and validates that the sequence produces the requested constant.
- `gen1`, `gen2`, and `gen3` recursively search the space of shifts, adds, and subtracts.
- The recipe encoding uses letters for shifts and `+`/`-` for arithmetic between two virtual registers.
- `hintab` lists constants the search misses or would not find within the desired bounds; `hintabsize` exports its length.

Filesystem relevance: indirect compiler optimization.
