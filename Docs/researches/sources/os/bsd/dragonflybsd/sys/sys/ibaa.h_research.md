# File Research: sources/os/bsd/dragonflybsd/sys/sys/ibaa.h

`ibaa.h` defines state structures and macros for two pseudo-random/state algorithms, without include guards.

It sets `ALPHA`, `SIZE`, `MASK`, `ind(x)`, and `barrel(a)` macros, then defines `struct ibaa_state` with memory/results arrays, accumulator fields, byte index, and memory index.

It also defines `L15_STATE_SIZE` and `struct l15_state` with byte state and indices. The file assumes required integer types are already visible to the includer.
