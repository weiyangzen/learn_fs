# File Research: sources/os/plan9/9front/sys/src/cmd/9l/asmout.c

This file is the Power64 machine-code encoder for `9l`. It converts an already matched `Prog` plus `Optab` entry into one to five 32-bit instruction words or raw data words.

Key routines and structures:
- Opcode-construction macros such as `OPVCC`, `AOP_RRR`, `AOP_IRR`, `LOP_RRR`, `OP_BR`, `OP_BC`, and `OP_RLW` encode PowerPC instruction fields.
- `getmask`, `maskgen`, `getmask64`, and `maskgen64` validate and convert 32/64-bit masks for rotate-and-mask instructions.
- `asmout` handles `Optab.type` cases, including pseudo-ops, register moves, arithmetic/logical operations, memory loads/stores, branches, large constants, 64-bit constants, special registers, floating point, traps, compares, indexed forms, cache/TLB operations, and dynamic relocation forms.
- `oprrr`, `opirr`, `opload`, `oploadx`, `opstore`, and `opstorex` map assembler opcodes to PowerPC primary/extended opcodes.

Important interactions:
- Called from `asm.c:asmb` after instruction sizes and operand classes are fixed.
- Uses `regoff`/`vregoff` from `span.c` to obtain classified offsets.
- Calls `dynreloc` for DLM relocation records where required.
- Relies on `Optab.type` values defined by `optab.c`.

Research notes:
- Large constants are synthesized through `ADDIS`/`ORI`, temporary register use, and 64-bit rotate/insert forms.
- Conditional and unconditional branches validate alignment and displacement range.
- Several macro instructions, such as remainder, expand to multi-instruction sequences using `REGTMP`.
