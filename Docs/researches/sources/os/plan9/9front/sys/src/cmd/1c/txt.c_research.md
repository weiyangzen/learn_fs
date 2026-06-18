# File Research: sources/os/plan9/9front/sys/src/cmd/1c/txt.c

Target initialization and low-level instruction selection/emission helpers for `1c`.

Key responsibilities:
- `ginit` initializes target identity, register pools, move/conversion tables, opcode tables, string/static/rathole symbols, and 64-bit support.
- `gclean` verifies register balance, flushes string data, emits globals, and writes final object code.
- `oinit` maps generic C operations and types to 68000/68881 opcodes.
- `nextpc`, `prg`, `gpseudo`, and `gpseudotree` allocate and emit `Prog` records.
- `naddr` converts compiler AST nodes into target `Adr` operands.
- `regalloc`, `regaddr`, `regpair`, `regret`, and `regfree` manage scratch data/address/FP registers.
- `gmove` handles type conversions, extension/truncation, integer/FP conversions, unsigned-to-FP edge cases, and FPCR rounding control.
- `gopcode` emits typed opcodes and bitfield metadata.
- `asopt` applies small local emission optimizations such as `MOV $0` to `CLR`, stack push via `PEA`, and small immediate materialization.
- Defines target width and cast tables.

Notable details:
- `exreg` reserves external register candidates near the high end of each register class.
- The backend explicitly initializes A6/A7 as address registers in use.
