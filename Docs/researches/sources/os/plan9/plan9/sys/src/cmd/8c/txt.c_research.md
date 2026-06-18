# File Research: sources/os/plan9/plan9/sys/src/cmd/8c/txt.c

Purpose: main 386 C compiler text/code emission layer.

Key behavior: `ginit` initializes target identity, pseudo nodes, register state, type widths, and 64-bit support; `gclean` emits globals and final `AEND`. Register helpers allocate/free integer, FPU, and register-pair nodes. `naddr` converts AST address nodes into 8.out operands. `gmove`, `fgopcode`, and `gopcode` map C operations/conversions to 386/x87 instructions. `gins`, `gbranch`, `patch`, and `gpseudo` create instruction records.

Integration notes: consumes `xcom`/`OINDEX` state from `sgen.c`, serializes via `swt.c`, and relies on `8.out.h` opcodes recognized by `8l`. High-risk areas are x87 rounding-control conversion sequences, unsigned integer/float conversions, stack temporary allocation, and `idx` global use for indexed operands.
