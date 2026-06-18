# File Research: sources/os/plan9/9front/sys/src/cmd/2c/mul.c

Purpose: multiplication-by-constant expansion table for the 68020 compiler backend.

Key contents:
- `Multab multab[]` maps selected positive integer constants to compact operation strings that synthesize multiplication using moves, adds, subtracts, and shifts.
- The comment defines the mini-language:
  - `0` copy register,
  - `1`/`2` subtract variants,
  - `3`/`4` add variants,
  - `5`/`6` self/add shifts by one,
  - letters encode larger shifts on either temporary register.
- `multabsize` exposes table length for binary search in `mulcon1()` in `swt.c`.

Research notes:
- Used by `cgen.c` for `OMUL`/`OLMUL` and by `shlcon()` for constant left shifts.
- The table favors hand-tuned short sequences for common constants up to 100 and selected larger round constants.
