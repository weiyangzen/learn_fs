# File Research: sources/os/plan9/9front/sys/src/cmd/awk/maketab.c

Generates the awk token dispatch table used by the runtime executor.

Key responsibilities:
- Reads `y.tab.h` token definitions.
- Emits C source containing `printname[]`, `proctab[]`, and `tokname`.
- Maps grammar token IDs to runtime function names such as `arith`, `assign`, `boolop`, `program`, `getline`, `printstat`, and `jump`.
- Uses `nullproc` for tokens without runtime implementations.

Important interfaces:
- Consumes `y.tab.h`.
- Emits generated C intended to be compiled into awk.
- Depends on the `FIRSTTOKEN..LASTTOKEN` range.

Notes:
- This is a build-time helper, not part of awk runtime execution.
