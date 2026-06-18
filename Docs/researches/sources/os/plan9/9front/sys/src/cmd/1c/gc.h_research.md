# File Research: sources/os/plan9/9front/sys/src/cmd/1c/gc.h

Primary backend header for the Plan 9 `1c` 68000 compiler.

Key contents:
- Defines target type sizes: 8-bit char, 16-bit short, 32-bit int/long/pointer, 64-bit vlong/double.
- Declares backend IR/address structures `Adr`, `Prog`, `Txt`, `Case`, register-flow structures `Reg`, `Rgn`, `Var`, constant-multiply table `Multab`, and switch case helper `C1`.
- Defines liveness/register-allocation cost constants and bitset helper macros.
- Declares all backend globals: instruction lists, register usage arrays, flow graph nodes, data/string symbols, cases, stack offsets, variables, and optimization metadata.
- Prototypes code generation, register allocation, peephole optimization, switch/bitfield helpers, object output, alignment, and 64-bit support hooks.
- Installs vararg formatting checks for backend debug printers.

Role in system:
- Shared by all `cmd/1c` backend files and ties the generic Plan 9 C front end to the 68000 object format.
