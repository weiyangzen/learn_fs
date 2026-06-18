# File Research: sources/os/plan9/plan9/sys/src/cmd/cc/bits.c

Small bitset utility module for the C compiler. `Bits` is a fixed-width array defined in `cc.h`.

Functions implement bitwise union `bor`, intersection `band`, any-bit test `bany`, equality `beq`, first-set-bit number `bnum`, single-bit construction `blsh`, and membership test `bset`. A `bnot` implementation is present but disabled in comments.

These utilities support compiler data-flow or register/variable-set style operations elsewhere in the compiler.
