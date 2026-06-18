# File Research: sources/os/plan9/9front/sys/src/cmd/6l/asm.c

- Role: Final executable/object image writer for the amd64 linker `6l`.
- `entryvalue()` resolves numeric or symbolic entry point, validating that symbolic entries are text unless dynamic-load-module data semantics apply.
- Provides endian-specific byte writers: `wputl()`, `wput()`, `lput()`, `llput()`, `lputl()`, and `strnput()`.
- `asmb()` writes text bytes by calling `asmins()` over each `Prog`, verifies phase consistency, writes data blocks, symbols, line tables, optional dynamic tables, and finally writes executable headers.
- Supports Plan 9 header type 2 fat header, Plan 9 32-bit header type 3, and ELF32-style header type 5 with amd64/386 machine selection.
- `datblk()` constructs initialized data blocks from DATA/INIT/DYNT records, handling float constants, string constants, integer/address constants, duplicate-init checks, symbol relocation, and endianness maps.
- `cflush()` flushes buffered output bytes.
- `rnd()` rounds signed 64-bit values to positive alignment boundaries.
