# File Research: sources/os/plan9/9front/sys/src/cmd/vc/v.out.h

Purpose: MIPS object-code constants for the Plan 9 `vc` compiler and related tools.

Key behavior:
- Defines symbol/register counts and text flags.
- Defines MIPS integer and floating register assignments used by the backend ABI.
- Enumerates MIPS opcodes, including core arithmetic/branch/load/store, FP operations, MIPS64-like extensions, dynamic/init pseudo-ops, switch pseudo-ops, and object markers.
- Defines address type/name constants such as branch, memory, extern/static/auto/param, constants, registers, FP registers, file names, and vlong constants.
- Defines `SYMDEF` and the simulated IEEE double layout used for object encoding.

Dependencies:
- Included by `gc.h` and object emitters.

Notable details:
- Register names encode Plan 9 backend conventions: stack is R29, static base is R30, link is R31, and R0 is the zero register.
