# File Research: sources/os/plan9/plan9/sys/src/cmd/vl/asm.c

Purpose: MIPS linker backend assembly/output emitter.

Key behavior:
- Provides endian-aware byte/half/word/vlong output helpers.
- `entryvalue` resolves entry point names or numeric addresses.
- Emits multiple output header formats: Plan 9 boot images, Plan 9 MIPS a.out-style headers, and ELF32/ELF64 variants.
- `asmb` writes text instructions, padding/text holes, data, symbols, line tables, and final headers.
- `asmsym` emits text/data/bss/file/frame/auto/param symbols.
- `asmlc` emits compressed line-number tables.
- `datblk` materializes initialized data/string blocks from linker data progs with endian conversion.
- `asmout` converts linker `Prog` instructions to one or more MIPS machine words across many instruction templates.
- `oprrr`, `opirr`, and `vshift` map assembler opcodes to MIPS encoding fields.

Dependencies:
- Uses linker IR/state from `l.h`, opcode tables from the MIPS assembler headers, ELF helpers, symbol table, data progs, and output file descriptor `cout`.

Notable details:
- Supports both big- and little-endian MIPS output.
- Contains several synthesized-instruction paths for large constants/addresses and floating-point loads/stores.
- `opirr` aborts after reporting an unknown immediate-format opcode.
