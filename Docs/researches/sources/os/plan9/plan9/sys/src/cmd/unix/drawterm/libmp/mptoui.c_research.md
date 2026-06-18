# File Research: sources/os/plan9/plan9/sys/src/cmd/unix/drawterm/libmp/mptoui.c

Defines unsigned `uint` conversion helpers `uitomp(uint i, mpint *b)` and `mptoui(mpint *b)`. It assumes `mpdigit` can hold a `uint` and uses the same `mpassign(mpzero, b)` reset pattern as the signed conversion file.

`uitomp` allocates a destination if needed, marks nonzero values with `top = 1`, and stores the value in the first limb.

`mptoui` clamps negative inputs to `0` and clamps values needing more than one limb or exceeding `MAXUINT` to `MAXUINT`. Since `MAXUINT` is the full `uint` range, the overflow path mainly guards multi-limb values.
