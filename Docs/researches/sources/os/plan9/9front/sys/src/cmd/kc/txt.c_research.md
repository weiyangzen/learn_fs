# File Research: sources/os/plan9/9front/sys/src/cmd/kc/txt.c

Instruction emission, register allocation helpers, calling convention support, moves/conversions, branches, pseudo-ops, and target type tables for the SPARC C compiler backend. `ginit` initializes target globals, special nodes (`.safe`, `.rathole`, `.ret`), register reservations, and 64-bit support; `gclean` flushes pending strings/globals and writes `AEND`.

`gmove` is the large conversion/move matrix for integer, pointer, float, double, memory, and constant cases, including special floating constants and rathole-mediated conversions. `gopcode` maps frontend operations to SPARC opcodes and compare-branch pairs. The file also defines argument placement, stack temporaries, external register assignment, small-immediate tests, and target width/cast compatibility tables.
