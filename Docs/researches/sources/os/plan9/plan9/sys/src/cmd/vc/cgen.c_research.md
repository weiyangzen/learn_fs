# File Research: sources/os/plan9/plan9/sys/src/cmd/vc/cgen.c

Purpose: expression, boolean, lvalue, and structure code generation for the Plan 9 MIPS C compiler backend.

Core functions:
- `cgen` emits code for scalar expressions, assignments, arithmetic, calls, casts, conditionals, increments, bitfields, and loads/stores.
- `reglcgen` and `lcgen` compute lvalue addresses.
- `bcgen` and `boolgen` emit branch/value boolean code with short-circuiting.
- `sugen` emits structure/union copies, structure literals, function-returned structs, and temporary handling.
- `layout` copies small groups of longwords and supports unrolled loop copies for larger structures.

Integration points:
- Uses register allocation and instruction emission from `txt.c`.
- Uses bitfield helpers and multiply-constant optimization from `swt.c`/`mul.c`.
- Depends on complexity/addressability from `sgen.c`.

Risks:
- Correctness relies on `complex`/`addable` metadata and function-call complexity (`FNX`) to avoid clobbering operands.
- Struct copy logic creates non-interruptible temporaries (`nodrat`) and requires stack/rathole sizing to be accurate.
- Many branches depend on type classes (`typefd`, `typesuv`, `typeu`); extending types requires coordinated changes across backend files.
