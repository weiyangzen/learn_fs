# File Research: sources/os/plan9/9front/sys/src/cmd/8l/asm.c

This file writes final executable output for the 386 linker.

Key responsibilities:
- `entryvalue()` resolves numeric or symbolic entry points, validating that symbolic entries are text unless dynamic linking permits data adjustment.
- Provides endian-specific byte emitters: `wputl()`, `wput()`, `lput()`, `lputl()`, and fixed-width `strnput()`.
- `asmb()` is the main output pass:
  - Seeks past headers.
  - Emits text by walking `firstp`, checking phase consistency, calling `asmins()`, and flushing instruction bytes.
  - Emits data blocks with `datblk()`.
  - Emits symbols, stack/line tables, and dynamic-linking data when enabled.
  - Writes final headers for multiple `HEADTYPE`s: historical/COFF-like, Unix COFF, Plan 9, DOS COM/EXE, and 32-bit ELF.
- `cflush()` flushes buffered output.
- `datblk()` materializes data initializers, floats, strings, addresses, relocations, and duplicate initialization checks.
- `rnd()` rounds values to alignment boundaries.

Integration points:
- Depends on `l.h` linker globals and `asmins()` machine instruction encoding.
- Uses data layout from `dodata()`/`doinit()` and symbol tables built by object loading.
- Supports dynamic relocations through `dynreloc()` and `dlm`.

Risks and invariants:
- Phase errors indicate span/emission size mismatches.
- Header math is highly format-specific and tied to `INITTEXT`, `INITDAT`, `HEADR`, and `INITRND`.
- `datblk()` must honor Plan 9 byte-order maps (`inuxi*`, `fnuxi*`) for portable output.
