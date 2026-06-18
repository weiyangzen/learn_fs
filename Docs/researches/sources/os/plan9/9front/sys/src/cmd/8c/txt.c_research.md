# File Research: sources/os/plan9/9front/sys/src/cmd/8c/txt.c

This is the 386 backend instruction emitter, register allocator, argument placer, move/conversion generator, and backend initializer/finalizer.

Key responsibilities:
- `ginit()` initializes architecture identity, listing formats, code stream state, special nodes, string state, 64-bit support, and register availability.
- `gclean()` validates register balance, flushes string literals, emits `GLOBL` records, writes `AEND`, and calls `outcode()`.
- `nextpc()` allocates new `Prog` records.
- `gargs()`/`garg1()` evaluate and place call arguments, using temporaries for function-valued subexpressions.
- Provides register helpers: `regalloc()`, `regfree()`, `regret()`, `regsalloc()`, `regaalloc()`, `regind()`, and `nodreg()`.
- `naddr()` translates compiler `Node` addressing forms into object `Adr` operands.
- `gmove()` emits loads, stores, integer conversions, float conversions, and float/integer conversion sequences.
- `gins()`, `gopcode()`, `fgopcode()`, `gbranch()`, `patch()`, and `gpseudo()` are the primary instruction emission APIs.
- Defines type widths and cast masks for the 386 ABI.

Integration points:
- Used by nearly all code-generation files.
- Consumes addressability and indexed-address decisions from `sgen.c`.
- Emits opcodes defined in `8.out.h` into `Prog` records later optimized and serialized.

Risks and invariants:
- Register accounting is manual; leaks are reported in `gclean()`.
- Float conversion uses x87 control-word manipulation when truncation behavior is required.
- `doindex()` relies on global `idx` state set by `sgen.c`.
