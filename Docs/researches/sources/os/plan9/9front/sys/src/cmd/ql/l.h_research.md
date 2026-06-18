# File Research: sources/os/plan9/9front/sys/src/cmd/ql/l.h

This is the central private header for the PowerPC linker `ql`.

Key definitions:
- Core structures: `Adr`, `Prog`, `Sym`, `Auto`, and `Optab`.
- Operand classes `C_*`, symbol types `S*`, program mark flags, relocation bit layout constants, and global linker limits.
- Global linker state: buffers, header parameters, symbol hash table, instruction chains, data chains, debug flags, sizes, current text/function context, import/export state, and dynamic-linking state.
- Declarations for all linker passes and helpers across `asm.c`, `asmout.c`, `obj.c`, `pass.c`, `span.c`, `sched.c`, and `list.c`.

Important conventions:
- `P` and `S` are null sentinels for `Prog*` and `Sym*`.
- `Adr` overlays offsets, string constants, and IEEE constants.
- `Prog` includes `from`, `from3`, `to`, branch links, scheduling marks, opcode cache, line number, and register fields.
- `Optab` rows describe assembler operand classes, encoding type, output size, and default base register.

Implementation notes:
- The header makes heavy use of Plan 9 `EXTERN` style global declarations.
- It installs custom format checking pragmas for instruction, address, symbol, and class printers.
