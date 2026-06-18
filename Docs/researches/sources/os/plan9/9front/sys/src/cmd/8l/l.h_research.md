# File Research: sources/os/plan9/9front/sys/src/cmd/8l/l.h

This is the shared private header for the 386 linker `8l`.

Key responsibilities:
- Includes Plan 9 libc/bio headers, 386 object definitions, and shared compatibility declarations.
- Defines linker-side structures:
  - `Adr` with unions for offsets, string constants, branches, IEEE constants, autos, and symbols.
  - `Prog` for linked instructions, pc, branch/work pointers, cached operand classes, and marks.
  - `Auto` for automatic variables.
  - `Sym` for linker symbols and metadata.
  - `Optab` for instruction encoding table entries.
- Defines symbol types, hash sizes, IO sizes, history limits, operand classes (`Y*`), encoding forms (`Z*`), prefix constants, and relocation bit allocations.
- Declares global linker state for headers, text/data sizes, buffers, symbols, libraries, pc, debug flags, instruction bytes, endian maps, dynamic linking/import/export state, and current instruction/text pointers.
- Declares functions used across linker passes: object loading, library loading, span, patch/follow, data layout, symbol output, relocation, instruction encoding, diagnostics, and conversions.

Integration points:
- Included by `8l` implementation files such as `asm.c`, `span.c`, object readers, and instruction encoders.
- Shares opcode and operand numbering with `8a`/`8c` via `8.out.h`.
- The `cput` macro and output buffer globals are consumed by `asm.c`.

Risks and invariants:
- Operand and encoding class enums must stay aligned with optab tables.
- Many fields have phase-specific meanings, for example `Prog.width` as fake DATA width and `Adr.cond` as an unused branch-shaped union member.
- Dynamic-linking state is globally shared and format-sensitive.
