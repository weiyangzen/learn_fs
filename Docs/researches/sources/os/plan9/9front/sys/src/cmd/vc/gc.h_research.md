# File Research: sources/os/plan9/9front/sys/src/cmd/vc/gc.h

Purpose: Shared header for the `vc` MIPS compiler backend.

Key behavior:
- Includes the generic C compiler header and MIPS object-format definitions.
- Defines target type sizes for 32-bit MIPS and backend constants.
- Declares core backend structures: `Adr`, `Prog`, `Case`, `C1`, `Multab`, `Hintab`, `Var`, `Reg`, and `Rgn`.
- Declares global compiler/backend state, including program lists, case lists, register tracking, variable bitsets, dataflow graph nodes, and optimization regions.
- Defines dataflow macros for loads, stores, bit membership, and cost constants.
- Prototypes codegen, register allocation, peephole, switch, bitfield, output, formatting, and optimizer functions.

Dependencies:
- Depends on generic `../cc/cc.h` and MIPS-specific `v.out.h`.

Notable details:
- `Reg` stores both control-flow edges and backward/forward liveness/synchrony bitsets for global register optimization.
