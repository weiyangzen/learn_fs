# File Research: sources/os/plan9/9front/sys/src/cmd/ql/asmout.c

This file maps linker pseudo-instructions and selected `Optab` instruction forms into PowerPC machine words.

Key responsibilities:
- Defines PowerPC opcode construction macros such as `OPVCC`, `AOP_RRR`, `AOP_IRR`, branch encoders, and rotate-mask encoders.
- `asmout()` is the central encoder. It switches on `Optab.type` and emits one to five 32-bit words for each instruction form.
- Handles register-register arithmetic, immediate arithmetic, loads/stores, indexed memory operations, branches, condition-register moves, SPR/MSR/FPSCR moves, traps, rotate-mask instructions, cache/TLB operations, and floating-point instructions.
- Expands macro forms such as signed byte loads, large constants, large-address loads/stores, branch-to-register via LR, and remainder via divide/multiply/subtract.
- Supports DLM relocation emission through `reloc()` and `dynreloc()` calls for split and absolute relocations.

Opcode tables:
- `oprrr()` maps register-register and many special/floating opcodes.
- `opirr()` maps immediate and branch opcodes.
- `opload()`, `oploadx()`, `opstore()`, and `opstorex()` map load/store variants.

Implementation notes:
- `getmask()` and `maskgen()` convert bit masks into PowerPC rotate-mask fields.
- `aflag` mode returns a synthesized first instruction word for scheduler/analysis use without emitting output.
- It diagnoses illegal R0 literal operations when `r0iszero` semantics are active.
