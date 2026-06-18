# File Research: sources/os/plan9/plan9/sys/src/cmd/5c/txt.c

## Scope

ARM code emission support for `5c`: initialization, register allocation, address conversion, moves, opcodes, branches, pseudo-ops, and type tables.

## Behavior

- `ginit()` initializes target identity, pseudo nodes, reserved registers, `.safe`, `.rathole`, `.ret`, and 64-bit codegen support.
- `gclean()` checks leaked registers, flushes strings, emits globals, appends `AEND`, and calls `outcode()`.
- Provides temporary and argument register/stack allocation helpers.
- Converts AST nodes to ARM object `Adr` values with `naddr()`/`raddr()`.
- `gmove()` handles loads, stores, integer/floating conversions, sign/zero extension, and unsigned-to-float expansion.
- `gopcode()` maps generic C operations to ARM opcodes and branch conditions.
- Defines scalar type widths and cast compatibility masks.

## Dependencies

Uses `gc.h`, ARM register constants, compiler globals, type tables, `com64init()`, `outcode()`, and Plan 9 object format definitions.

## Risks And Invariants

- Register allocation is simple reference-counted global state; imbalance is caught only at cleanup or `regfree()` diagnostics.
- Some conversions intentionally emit longer compatibility sequences for old ARM/VFP behavior.
- `sconst()` currently accepts most integer constants and delegates actual immediate fit to the linker.
- Stack and argument layout is tied to `align()` in `swt.c`.
