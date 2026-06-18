# File Research: sources/os/plan9/plan9/sys/src/cmd/kc/enam.c

This file defines `anames[]`, the textual names for SPARC backend opcode enum values from `k.out.h`.

The array covers integer arithmetic/logical ops, branches, coprocessor ops, data/pseudo ops, floating-point ops, loads/stores, traps, `TEXT`, `GLOBL`, `HISTORY`, `NAME`, `END`, dynamic/init/signature records, and `LAST`.

It is used by listing and diagnostic formatting, especially `%A` conversion in `list.c`. Correct ordering must remain synchronized with `enum as` in `k.out.h`.
