# File Research: sources/os/plan9/plan9/sys/src/cmd/qc/gc.h

Purpose: Central target-specific header for the Plan 9 PowerPC C compiler backend.

Key contents:
- Includes common C compiler definitions and PowerPC object definitions.
- Defines C type sizes for this target.
- Declares core backend structures: `Adr`, `Prog`, `Case`, `C1`, `Multab`, `Hintab`, `Var`, `Reg`, and `Rgn`.
- Defines instruction, register-allocation, data-flow, loop, and region globals.
- Declares helpers for code generation, text emission, register allocation, moves, addressing, constants, branches, switch lowering, bitfields, external data, listing formats, register optimization, peephole optimization, copying/substitution, register bit conversions, and 64-bit comparison lowering.
- Defines data-flow macros such as `BLOAD`, `BSTORE`, `LOAD`, and `STORE`.

Dependencies and integration:
- Included by target backend source files such as `cgen.c`.
- Interfaces with shared compiler frontend `../cc/cc.h` and target object format `../qc/q.out.h`.

Risks and notes:
- Header is both API and global-state declaration file using `EXTERN`.
- Constants like `NRGN`, register counts, and type sizes are baked into backend behavior.
