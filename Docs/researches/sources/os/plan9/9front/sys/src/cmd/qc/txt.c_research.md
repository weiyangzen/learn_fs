# File Research: sources/os/plan9/9front/sys/src/cmd/qc/txt.c

Low-level Power instruction selection and emission layer for the C compiler backend.

Key responsibilities:
- `ginit` initializes target globals, pseudo nodes, rathole/string storage, register reservations, and 64-bit codegen.
- `gclean` validates register balance, flushes strings, emits globals and `AEND`, and calls `outcode`.
- `nextpc`, `gins`, `gins3`, and `gins4` allocate and populate `Prog` instructions.
- `gargs`/`garg1` implement argument passing and temporary spilling for complex call arguments.
- `regalloc`, `regfree`, `regsalloc`, `regaalloc`, `regret`, and related helpers manage scratch, return, stack, and argument registers.
- `naddr` and `raddr` translate compiler `Node` addressing into object `Adr` operands.
- `gmove` handles loads, stores, casts, integer/float moves, float conversions, constants, and vlong register-pair moves.
- `gopcode` maps C operators to Power opcodes; `gopcode64`, `gori64`, and `gandi64` implement 64-bit arithmetic/logical/shift operations over register pairs.
- `gbranch`, `patch`, `gpseudo`, `sconst`, `uconst`, `exreg`, `ewidth`, and `ncast` provide branch patching, pseudo-ops, immediates, external registers, and type metadata.

Dependencies and coupling:
- Central implementation behind `cgen.c`, `swt.c`, and `reg.c`.
- Uses object opcodes/address types from `q.out.h` and ABI alignment from `swt.c`.

Notable behavior:
- Several float/integer conversions are hand-built via Power floating constants and stack temporaries.
- `R0ISZERO` influences zero constant emission.
