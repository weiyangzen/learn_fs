# File Research: sources/os/plan9/plan9/sys/src/cmd/6c/mul.c

This file optimizes multiplication by integer constants. It searches for short sequences of shifts, adds, subtracts, and scaled-address calculations that replace a general multiply instruction.

`mulparam` analyzes a multiplier and chooses an algorithm from predefined forms. `mulgen1` uses cached multiplier parameters and emits selected instruction sequences. `genmuladd` builds amd64 indexed-address expressions to compute `base + index*scale` through `LEA`-style address generation. `shiftit` chooses an add for shift-by-one or a shift instruction otherwise.

If no compact sequence is found, `mulgen` falls back to normal multiply generation. Helpers such as `lowbit`, `m0`, `m1`, and `m2` support constant decomposition.

Filesystem relevance is performance-oriented: compiled filesystem and kernel code often contains offset, block, and structure-size arithmetic, and this backend can lower some constant multiplies into cheaper address arithmetic.
