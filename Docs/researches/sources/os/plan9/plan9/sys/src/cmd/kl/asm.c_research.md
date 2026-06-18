# File Research: sources/os/plan9/plan9/sys/src/cmd/kl/asm.c

Read fully: 1242 lines, 26122 bytes. SHA-256 prefix: `06243f0af240915d`.

This is the final assembly/output backend for the Plan 9 SPARC linker `kl`. It writes text, data, symbols, line tables, and executable headers. `asmb()` drives emission: it seeks past the header, walks `firstp`, validates phase/PC consistency, calls `oplook()` and `asmout()` for instruction encoding, writes data blocks with `datblk()`, emits symbols with `asmsym()`, emits line number compression with `asmlc()`, then rewrites the executable header for boot, Plan 9, or Javastation formats.

Important routines:
- `entryvalue()` resolves `INITENTRY` as either numeric address or text symbol.
- `lput()`/`cflush()` implement buffered big-endian word output.
- `putsymb()` serializes Plan 9 symbol-table entries, including filename symbols.
- `datblk()` materializes initialized data from `ADATA`/`AINIT`/`ADYNT`, handling integer, string, and IEEE float constants with host-to-target byte order tables.
- `asmout()` maps `Optab.type` cases to SPARC encodings, including synthetic long constant/address sequences, loads/stores, ASI accesses, branches/calls, floating-point operations, division/modulus expansions, and annulled delay-slot optimizations.
- `opcode()` maps linker opcodes to SPARC op/op2/op3/floating/trap/branch encodings.

Dependencies are almost entirely linker-global state from `l.h`: `firstp`, `datap`, `curtext`, `autosize`, `textsize`, `datsize`, `symsize`, `lcsize`, endian tables, and debug flags. It depends on `oplook()`/`Optab` from `span.c`/`optab.c`, symbol lookup from `obj.c`, and IEEE conversion helpers.

Risk notes: encoding is table-driven but many `asmout()` cases assume exact operand classes and register conventions. Branch-delay-slot filling calls `asmout(..., aflag)` speculatively and only works for encodings that can safely be lifted. Data initialization detects overlapping non-`AINIT` writes but uses a fixed scratch allowance (`n+100`).
