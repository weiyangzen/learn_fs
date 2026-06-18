# File Research: sources/os/plan9/plan9/sys/src/cmd/ql/asmout.c

PowerPC instruction encoder for the `ql` linker.

Key responsibilities:
- Defines bitfield macros for PowerPC instruction forms.
- Converts linker optab classes into one to five emitted instruction words.
- Encodes moves, arithmetic, logical operations, loads/stores, indexed forms, branches, condition-register operations, special-register moves, FPSCR operations, traps, rotate/mask operations, and pseudo-instruction expansions.
- Synthesizes large constants and long-offset memory references using `REGTMP`.
- Handles branch target validation and dynamic relocations.
- Implements helper opcode maps: register-register, immediate-register, load, indexed load, store, and indexed store.
- Supports standard PowerPC, floating point, embedded PowerPC MAC instructions, optional FP, paired/secondary FP, DCR access, and cache/control instructions.

Dependencies:
- Uses `l.h`, optab classification, `regoff`, `dynreloc`, output helpers from `asm.c`, and opcode enums from the PowerPC object format.

Notable risks:
- Encoding depends on exact optab type contracts.
- Some pseudo-instructions such as remainder are expanded into multi-instruction sequences.
- Large constants and long offsets can fail if operands already require `REGTMP`.
