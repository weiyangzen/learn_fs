# File Research: sources/os/plan9/plan9/sys/src/cmd/vc/gc.h

Purpose: shared backend header for the Plan 9 MIPS C compiler.

Key contents:
- Includes common C compiler definitions from `../cc/cc.h` and MIPS object definitions from `v.out.h`.
- Defines target sizes for MIPS: 1-byte chars, 4-byte ints/longs/pointers/floats, 8-byte vlongs/doubles.
- Defines backend structures: `Adr`, `Prog`, `Case`, `C1`, `Multab`, `Hintab`, `Var`, `Reg`, and `Rgn`.
- Declares global codegen/register-allocation state.
- Defines liveness and region-cost macros.
- Declares functions implemented by `sgen.c`, `cgen.c`, `txt.c`, `swt.c`, `list.c`, `reg.c`, and `peep.c`.
- Registers custom format verbs for instructions, addresses, bits, and symbols.

Integration points:
- Included by every `cmd/vc` C file in this group.
- Serves as the backend ABI among parser/common compiler code and target-specific emission code.

Risks:
- Many globals are shared mutable compiler state; backend routines assume single-threaded compilation.
- Register-region limits such as `NRGN` and `NVAR` constrain optimization on large functions.
