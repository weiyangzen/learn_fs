# File Research: sources/os/plan9/plan9/sys/src/cmd/kc/bits.c

This file provides bitset helpers for the SPARC C compiler backend. Active functions are `bany()`, `bnum()`, `blsh()`, and an older-style `Bconv()` formatter.

Several basic bit operations (`bor`, `band`, `bnot`, `beq`, `bset`) are present but commented out, implying equivalent macros or shared implementations exist elsewhere.

`bnum()` returns the first set bit index using `bitno()` and reports a compiler diagnostic if called on an empty set. `blsh()` constructs a single-bit `Bits` value. `Bconv()` formats variable bitsets by resolving entries through the global `var[]` table.

The functionality supports liveness/register allocation diagnostics. Note that `list.c` also defines a modern `Bconv(Fmt*)`, so this file appears to be legacy or build-conditional in relation to newer Plan 9 fmt APIs.
