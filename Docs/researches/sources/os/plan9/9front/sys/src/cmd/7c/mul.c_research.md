# File Research: sources/os/plan9/9front/sys/src/cmd/7c/mul.c

Constant-multiplication recipe generator. It finds short shift/add/sub sequences that can replace multiplication by constants.

Key functions:
- `mulcon0` normalizes negative constants, checks a small cache, consults the exception hint table, recursively searches for a recipe up to `maxmulops`, and handles trailing power-of-two factors.
- `docode` interprets hint strings into concrete two-character encoded operations while tracking two virtual registers.
- `gen1`, `gen2`, and `gen3` recursively search the space of shifts, additions, and subtractions.
- `hintab` contains sorted exception recipes for constants the generic search fails to find under the operation limit.
- `hintabsize` exports the table length.

Recipe encoding:
- Letters `a` and up represent left shifts by letter offset.
- `+` and `-` represent add/sub combinations.
- The following digit encodes which virtual source/destination registers are used.

Important interaction:
- `swt.c:mulcon` consumes `Multab.code` and emits actual backend operations.

Filesystem relevance: indirect compiler optimization.
