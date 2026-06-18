# File Research: sources/os/plan9/plan9/sys/src/cmd/unix/drawterm/libmp/mptoi.c

Provides signed `int` conversion helpers `itomp(int i, mpint *b)` and `mptoi(mpint *b)`. The file assumes `mpdigit` is at least as large as `int`, resets destination values with `mpassign(mpzero, b)`, and writes the integer magnitude into the first limb.

`itomp` allocates when needed, sets `top = 1` for nonzero inputs, stores negative inputs as positive magnitude with `sign = -1`, and otherwise stores the unsigned magnitude directly.

`mptoi` is saturating: positive values larger than `MAXINT` or requiring more than one limb return `MAXINT`; negative values larger than `MININT` magnitude or requiring more than one limb return `MININT`. It depends on the `MAXINT`/`MININT` macros from `dat.h`.
